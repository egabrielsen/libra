"""
Simple faucet server
Proxies mint requests to local client that owns association keys
"""
import decimal
import os
import platform
import random
import re
import sys

import flask
import pexpect


MAX_MINT = 10 ** 19  # 10 trillion libras


def create_client():
    if application.client is None or not application.client.isalive():
        ac_host = os.environ['AC_HOST']
        

        print("Connecting to ac on: {}".format(ac_host))
        cmd = "target/debug/cli --url {} -m {}".format(
            ac_host,
            "../config/mint.key")

        application.client = pexpect.spawn(cmd)
        application.client.delaybeforesend = 0.1
        application.client.expect("Please, input commands")


application = flask.Flask(__name__)
application.client = None
print(sys.version, platform.python_version())
create_client()


@application.route("/", methods=('POST',))
def send_transaction():
    address = flask.request.args['address']

    # Return immediately if address is invalid
    if re.match('^[a-f0-9]{64}$', address) is None:
        return 'Malformed address', 400

    try:
        amount = decimal.Decimal(flask.request.args['amount'])
    except decimal.InvalidOperation:
        return 'Bad amount', 400

    if amount > MAX_MINT:
        return 'Exceeded max amount of {}'.format(MAX_MINT / (10 ** 6)), 400

    try:
        create_client()
        application.client.sendline(
            "a m {} {}".format(address, amount / (10 ** 6)))
        application.client.expect("Mint request submitted", timeout=4)

        application.client.sendline("a la")
        application.client.expect(r"sequence_number: ([0-9]+)", timeout=2)
        application.client.terminate(True)
    except pexpect.exceptions.ExceptionPexpect:
        application.client.terminate(True)
        raise

    return application.client.match.groups()[0]