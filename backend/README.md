```
cd backend
py -m venv myenv
cd myenv/Scripts/activate
cd..
cd..
pip install requirements.txt
py -m uvicorn app.main:app --reload
```