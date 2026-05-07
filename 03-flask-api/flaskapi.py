from flask import Flask , request , jsonify
from classes.books import Library
app = Flask(__name__)

myLibrary = Library()


myLibrary.add_book("Romance", "White Rose", "Hubert Baciak", 2940, 2020)
myLibrary.add_book("Fantasy", "Ashes of the Moon", "Elena Voss", 412, 2018)
myLibrary.add_book("Sci-Fi", "Orbit of Silence", "Marek Nowak", 336, 2022)
myLibrary.add_book("Mystery", "The Glass Keyhole", "Clara Reed", 278, 2016)
myLibrary.add_book("Horror", "House Beneath the Lake", "Jon Bell", 198, 2019)
myLibrary.add_book("Fantasy", "The Last Ember", "Elena Voss", 521, 2021)
myLibrary.add_book("Romance", "Letters in Winter", "Hubert Baciak", 310, 2023)

myLibrary.printLibrary()



@app.route('/api/removeBook', methods = ['DELETE'])
def delete_book():
    data = request.get_json()
    try:
        author = data.get("author")
        book_id = data.get("book_id")
        if type(author) != str or author == "" or type(book_id) != int or book_id == 0 or not all(myLibrary.isBookExistingInEntries(author,book_id).values()):
            return jsonify({"error" : "Invalid types or empty data provided",
                            "description": "Correct format is authorName authorSurname,book_id"}), 400
        myLibrary.remove_book(data.get("author"),data.get("book_id"))
        return jsonify({"success": "Book was properly removed!",
                        "book": data}), 200
    except AttributeError:
        return jsonify({
            "error" : "Incorrect JSON provided"
        }), 400
 
        

@app.route('/api/books', methods = ['GET'])
def get_books():
    return jsonify(myLibrary.libraryContainer)
@app.route('/api/addBook', methods = ['POST'])
def add_book():
    data = request.get_json()
    try: 
        name = data.get("name")
        book_type = data.get("book_type")
        pages = data.get("pages")
        year = data.get("year")
        author = data.get("author")

        requiredAttributes = [name,book_type,pages,year,author]
        if any(attribute in ["",None] for attribute in requiredAttributes) :
            return jsonify({"error" : "Incorrect attributes provided",
                            "book" : data,
                            "description" : "Provided data can't be empty or in incorrect format"
                            }), 400
    except AttributeError:
        return jsonify({
            "error" : "Incorrect JSON provided"
        }), 400
    myLibrary.add_book(
        name=data["name"],
        book_type=data["book_type"],
        pages=data["pages"],
        year=data["year"],
        author=data["author"]
    )

    return jsonify({
        "message": "Book inserted successufuly!",
        "book": data
    }), 201


@app.route('/api', methods=['GET'])
@app.route('/api/', methods=['GET'])
def api_index():
    return jsonify({
        "message": "Available API endpoints",
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/books",
                "description": "Show all books"
            },
            {
                "method": "POST",
                "path": "/api/addBook",
                "description": "Add a new book"
            },
            {
                "method" : "DELETE",
                "path" : "/api/removeBook",
                "description" : "Remove a book"

            }
        ]
    })
if __name__ == '__main__':
    app.run(debug=True)