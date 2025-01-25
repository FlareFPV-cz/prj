pip install -r requirements.txt

cd backend
uvicorn main:app --reload

cd frontend
npm install
npm run dev 

openssl genpkey -algorithm RSA -out private.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in private.pem -out public.pem
openssl rsa -in private.pem -traditional -out private.pem