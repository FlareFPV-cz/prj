pip install -r requirements.txt

cd backend
uvicorn main:app --reload

cd frontend
npm install
npm run dev 