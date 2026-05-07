class Library:
    def __init__(self):
        self.libraryContainer = {}
        self.next_id = 1
    def add_book(self,book_type,name,author,pages,year):
        pages = int(pages)
        year = int(year)


        if author not in self.libraryContainer:
          self.libraryContainer[author] = []
        self.libraryContainer[author].append({
            "name" : name,
            "book_type" : book_type,
            "pages" : pages,
            "year" : year,
            "book_id" : self.next_id
        })
        self.next_id = self.next_id + 1
    def remove_book(self,author,book_id):
        if author not in self.libraryContainer:
            print("Author to remove, not found.")
            return
        books = self.libraryContainer[author]
        for book in books:
            if book["book_id"] == book_id:
                books.remove(book)
                return print("The book was successufuly removed!")
        return print("The book prompted to removal, wasn't found. Check for commas.")
    def edit_book(self,book_author_to_edit,book_id_to_edit,book_type = "", name = "", author = "", pages = 0 , year = 0):


        books = self.libraryContainer[book_author_to_edit]

        editingBook = None

        for book in books:
            if book["book_id"] == book_id_to_edit:
                editingBook = book
                print("Book to edit was found! Editing..")
                break
        if editingBook == None:
            return print("The book prompted to edit, wasn't found. Check for commas.")
        
        if book_type != "":
            editingBook["book_type"] = book_type
        if name != "":
            editingBook["name"] = name
        if pages != 0:
            editingBook["pages"] = int(pages)
        if year != 0:
            editingBook["year"] = int(year)
        
        if author != "" and author != book_author_to_edit:
            books.remove(editingBook)

            if author not in self.libraryContainer:
                self.libraryContainer[author] = []
            self.libraryContainer[author].append(editingBook)
        print("The book was successufuly edited")
    def printLibrary(self):
        print(f"This is available list of authors and their books: {self.libraryContainer}")
    def isBookExistingInEntries(self,author,book_id) -> dict:
        request_entry = {
        "was_correct_author_provided": False,
        "was_correct_book_id_Provided": False
        }

        for eachAuthor in self.libraryContainer:
            if eachAuthor == author:
                request_entry["was_correct_author_provided"] = True
                for eachBookId in self.libraryContainer[eachAuthor]:
                    if eachBookId["book_id"] == book_id:
                        request_entry["was_correct_book_id_Provided"] = True
                break
        return request_entry


        



