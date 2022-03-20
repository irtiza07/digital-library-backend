import psycopg2

from typing import List
from pydantic import BaseModel

import uvicorn
from fastapi import FastAPI, status

from fastapi.middleware.cors import CORSMiddleware


class Book(BaseModel):
    id: str = None
    volume_id: str
    title: str
    authors: str = None
    thumbnail: str = None
    state: int
    rating: int = None


class UpdateRatingRequstBody(BaseModel):
    volume_id: str
    new_rating: int


class UpdateStateRequestBody(BaseModel):
    volume_id: str
    new_state: int


app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/status")
async def check_status():
    return "Hello World!"


@app.get("/books", response_model=List[Book], status_code=status.HTTP_200_OK)
async def get_books():
    # Connect to our database
    conn = psycopg2.connect(
        database="exampledb", user="docker", password="docker", host="0.0.0.0"
    )
    cur = conn.cursor()
    cur.execute(
        "SELECT book.*, review.review_text FROM book LEFT JOIN review ON book.id=review.book_id ORDER BY id DESC"
    )
    rows = cur.fetchall()

    formatted_books = []
    for row in rows:
        formatted_books.append(
            Book(
                id=row[0],
                volume_id=row[1],
                title=row[2],
                subtitle=row[3],
                authors=row[4],
                thumbnail=row[5],
                snippet=row[6],
                state=row[7],
                rating=row[8],
                review_text=row[9],
            )
        )

    cur.close()
    conn.close()

    return formatted_books


@app.post("/books", status_code=status.HTTP_201_CREATED)
async def new_book(book: Book):
    # Connect to our database
    conn = psycopg2.connect(
        database="exampledb", user="docker", password="docker", host="0.0.0.0"
    )
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO book (volume_id, title, authors, thumbnail, state) VALUES ('{book.volume_id}', '{book.title}', '{book.authors}', '{book.thumbnail}', {book.state})"
    )

    cur.close()
    conn.commit()
    conn.close()
    return


@app.put("/books/update_rating", status_code=200)
async def update_rating(update_rating_body: UpdateRatingRequstBody):
    # Connect to our database
    conn = psycopg2.connect(
        database="exampledb", user="docker", password="docker", host="0.0.0.0"
    )
    cur = conn.cursor()
    cur.execute(
        f"UPDATE book SET rating={update_rating_body.new_rating} WHERE volume_id='{update_rating_body.volume_id}'"
    )

    cur.close()
    conn.commit()
    conn.close()
    return


@app.put("/books/update_book_state", status_code=200)
async def update_state(update_state_request_body: UpdateStateRequestBody):
    # Connect to our database
    conn = psycopg2.connect(
        database="exampledb", user="docker", password="docker", host="0.0.0.0"
    )
    cur = conn.cursor()
    print(update_state_request_body)
    cur.execute(
        f"UPDATE book SET state={update_state_request_body.new_state} WHERE volume_id='{update_state_request_body.volume_id}'"
    )

    cur.close()
    conn.commit()
    conn.close()
    return


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
