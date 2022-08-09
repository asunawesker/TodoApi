from pprint import pprint
from typing import Optional, List
from bson.objectid import ObjectId
from fastapi import FastAPI
from pydantic import BaseModel
import pymongo
import settings

app = FastAPI()


class Todo(BaseModel):
    _id: Optional[str]
    title: str
    description: str
    iscompleted: bool

class TodoUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    iscompleted: Optional[bool]

class Todos(BaseModel):
    List[Todo]

def get_db(db_name="TodoDB"):
    client = pymongo.MongoClient(settings.mongodb_uri, settings.port)
    db = client.get_database(db_name)
    return db


@app.get("/")
def home():
    return {"message": "Welcome Home!!"}

@app.get("/todo")
def get_todo():
    db = get_db()
    col = db.get_collection("Todo")
    emp = col.find({})
    
    todos = []
    for todo in emp:
        todo['_id'] = str(ObjectId(todo['_id']))
        todos.append(todo)
    return todos

@app.get("/todo/{id}", response_model=Todo)
def get_todo(id: str):
    db = get_db()
    col = db.get_collection("Todo")
    emp = col.find_one({"_id":ObjectId(id)})
    return emp


@app.post("/todo")
def create_todo(data: Todo):
    db = get_db()
    col = db.get_collection("Todo")
    new_emp = col.insert_one(data.dict())
    if new_emp.acknowledged:
        return {"message": f"Todo {data.title} created"}
    return {"message": "error occured while creating todo"}


@app.put("/todo/{id}")
def update_todo(id: str, data: TodoUpdate):
    db = get_db()
    col = db.get_collection("Todo")
    emp_dict = {k: v for k, v in data.dict().items() if v is not None}
    result = col.update_one({"_id": ObjectId(id)}, {"$set": emp_dict})
    if result.modified_count == 1:
        return {"message": f"todo updated."}
    return {"message": f"error occured while updating todo {data.title}"}


@app.delete("/todo/{id}")
def delete_todo(id: str):
    db = get_db()
    col = db.get_collection("Todo")
    result = col.delete_one({"_id":ObjectId(id)})
    if result.deleted_count == 1:
        return {"message": "Todo deleted"}
    return {"message": "error occured while deleting todo."}