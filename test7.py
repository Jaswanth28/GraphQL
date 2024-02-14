from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.asgi import GraphQL
from pymongo import MongoClient
from typing import List, Optional

client = MongoClient("mongodb://localhost:27017")
db = client["Books"]
lib = db["book"]
authr = db["authors"]
rev = db["reviews"]

@strawberry.type
class books:
    Book: Optional[str]=None
    Auth_id: Optional[int] =None
    Author: Optional[str] = None
    Reviews: Optional[List[str]] = None
    Writings:Optional[List[str]]=None

@strawberry.type
class auths:
    Author: str
    Auth_id:int

@strawberry.type
class Query:
    @strawberry.field
    def lib(self, book: Optional[str] = None, auth_id: Optional[int] = None) -> List[books]:
        query = {}
        if book:
            results = lib.find({"Book": book})
            books_list = []
            for result in results:
                auth_id = result.get("Auth_id")
                results2 = authr.find_one({"Auth_id": auth_id})
                res3 = rev.find({"Book": book})
                reviews_list = [res["Reviews"] for res in res3]
                res4=lib.find({"Auth_id":auth_id})
                others=[oss["Book"] for oss in res4]
                books_list.append(books(Book=result["Book"], Auth_id=auth_id, Author=results2["Author"], Reviews=reviews_list,Writings=others))
            return books_list
        if auth_id:
            results=authr.find({"Auth_id":auth_id})
            return [books(Author=result["Author"]) for result in results]
        results = lib.find(query)  
        return [books(Book=result["Book"],Auth_id=result["Auth_id"]) for result in results] 
    
    @strawberry.field
    def find_authors(self,author:Optional[str]=None,auth_id:Optional[int]=None)->List[auths]:
        query={}
        if author:
            ress=authr.find_one({"Author":author})
            return [auths(Author=ress["Author"],Auth_id=ress["Auth_id"])]
        if auth_id:
            ress=authr.find_one({"Auth_id":auth_id})
            return [auths(Author=ress["Author"],Auth_id=ress["Auth_id"])]
        ress=authr.find(query)
        return [auths(Author=outs["Author"],Auth_id=outs["Auth_id"]) for outs in ress]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(self,book:str,auth_id:int,author:Optional[str]=None)->str:
        existing_book = lib.find_one({"Book": book})
        if existing_book:
            return "Book already exists"
        else:
            if auth_id:
                existing_id=authr.find_one({"Auth_id":auth_id})
                if existing_id==None and author==None:
                    return "Enter new author name"
                else:
                    new_book={"Book":book,"Auth_id":auth_id}
                    lib.insert_one(new_book)
                    if existing_id==None and author!=None:
                        new_author={"Auth_id":auth_id,"Author":author}
                        authr.insert_one(new_author)
                    return "Book Added"
    @strawberry.mutation
    def add_review(self,book:str,reviews:str)->str:
        new_review={"Book":book,"Reviews":reviews}
        rev.insert_one(new_review)
        return "Review Added"

schema = strawberry.Schema(query=Query,mutation=Mutation)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/")
def index():
    return {"message": "Welcome to the service list"}

app.mount("/graphql", GraphQL(schema, debug=True))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test7:app", host="localhost", reload=True, port=8000)
