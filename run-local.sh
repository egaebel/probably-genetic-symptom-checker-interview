#!/bin/bash
./kill-local.sh

source backend/bin/activate
cd backend/src
python backend.py &
deactivate
cd ../..

sleep 3

cd frontend/
npm start &
cd ..
echo "Done! "
