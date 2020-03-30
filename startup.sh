#! /bin/bash 
install() {
  cd ~/
  echo "Setting up env..."
  source venv/bin/activate
  export FLASK_APP=libra/server.py
  export FLASK_ENV=development
  export AC_HOST=localhost
  export AC_PORT=8000
  echo "Starting libra net..."
  bash -c "exec -a libranet ./libra/target/debug/libra-swarm -c ~/config/ &"
  echo "Starting mint server..."
  bash -c "exec -a mintserver flask run --host=0.0.0.0 &"
}

install