import datetime


class BorrowRecord:
    def __init__(self, book, borrow_date=None, return_date=None):
        self.book = book
        self.borrow_date = borrow_date if borrow_date else datetime.datetime.now()
        self.return_date = return_date

    def is_returned(self):
        return self.return_date is not None

    def borrow_duration_days(self):
        end_date = self.return_date if self.is_returned() else datetime.datetime.now()
        return (end_date - self.borrow_date).days


class Book:
    def __init__(self, title, author, genre, isbn, is_issued=False):
        self.title = title
        self.author = author
        self.genre = genre
        self.isbn = isbn
        self.is_issued = is_issued
        self.ratings = []
        self.average_rating = 0.0

    def add_rating(self, rating):
        if 1 <= rating <= 5:
            self.ratings.append(rating)
            self.calculate_average_rating()
        else:
            print("Error: Rating must be between 1 and 5.")

    def calculate_average_rating(self):
        if self.ratings:
            self.average_rating = sum(self.ratings) / len(self.ratings)

    def is_available(self):
        return not self.is_issued


class User:
    def __init__(self, name, user_id, password, borrow_records=None):
        self.name = name
        self.user_id = user_id
        self.password = password
        self.borrow_records = borrow_records if borrow_records else []

    def borrow_book(self, book):
        record = BorrowRecord(book)
        self.borrow_records.append(record)

    def return_book(self, isbn):
        for record in self.borrow_records:
            if record.book.isbn == isbn and not record.is_returned():
                record.return_date = datetime.datetime.now()
                return record.book
        return None

    def has_borrowed_book_before(self, isbn):
        for record in self.borrow_records:
            if record.book.isbn == isbn and record.borrow_duration_days() > 1:
                return True
        return False


class Transaction:
    def __init__(self, library_system):
        self.library = library_system

    def issue(self, user_id, isbn):
        try:
            user = self.library.find_user_by_id(user_id)
            if not user:
                raise ValueError("Error: User ID not found.")
            book = self.library.find_book_by_isbn(isbn)
            if not book:
                raise ValueError("Error: Book ISBN not found.")
            if book.is_issued:
                raise ValueError("Error: Book is already issued.")

            # Secret Question Verification
            secret_answer = input("To verify, please enter your password: ")
            if secret_answer != user.password:
                raise ValueError("Error: Verification failed. Incorrect password.")

            # Issue the book
            book.is_issued = True
            user.borrow_book(book)
            print(f"Book '{book.title}' has been issued to {user.name}.")
        except ValueError as e:
            print(e)

    def return_book(self, user_id, isbn):
        try:
            user = self.library.find_user_by_id(user_id)
            if not user:
                raise ValueError("Error: User ID not found.")
            book = self.library.find_book_by_isbn(isbn)
            if not book:
                raise ValueError("Error: Book ISBN not found.")

            # Find corresponding BorrowRecord
            for record in user.borrow_records:
                if record.book.isbn == isbn and not record.is_returned():
                    record.return_date = datetime.datetime.now()
                    book.is_issued = False
                    print(f"Book '{book.title}' has been returned by {user.name}.")
                    print("Thank you for returning the book!")
                    return

            print(f"Error: {user.name} has not borrowed '{book.title}'.")

        except ValueError as e:
            print(e)


class LibrarySystem:
    def __init__(self):
        self.book_list = []
        self.user_list = []
        self.load_initial_data()

    def load_initial_data(self):
        # Initial Books
        initial_books = [
            {"title": "To Kill a Mockingbird", "author": "Harper Lee", "genre": "Fiction", "isbn": "9780061120084", "is_issued": False},
            {"title": "1984", "author": "George Orwell", "genre": "Dystopian", "isbn": "9780451524935", "is_issued": True},
            {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": "Fiction", "isbn": "9780743273565", "is_issued": False},
            {"title": "Sapiens: A Brief History of Humankind", "author": "Yuval Noah Harari", "genre": "Non-Fiction", "isbn": "9780062316097", "is_issued": False},
            {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "genre": "Fiction", "isbn": "9780316769488", "is_issued": True},
            {"title": "The Hobbit", "author": "J.R.R. Tolkien", "genre": "Fantasy", "isbn": "9780345339683", "is_issued": False},
            {"title": "Becoming", "author": "Michelle Obama", "genre": "Biography", "isbn": "9781524763138", "is_issued": False},
        ]

        for book in initial_books:
            self.book_list.append(Book(**book))

        # Initial Users
        initial_users = [
            {"name": "Alice Johnson", "user_id": "U001", "password": "alice123", "borrowed_books": ["9780451524935"]},  # 已借阅但未归还
            {"name": "Bob Smith", "user_id": "U002", "password": "bob_secure", "borrowed_books": []},
            {"name": "Charlie Davis", "user_id": "U003", "password": "charlie_pw", "borrowed_books": ["9780316769488"]},  # 已借阅但未归还
            {"name": "Diana Prince", "user_id": "U004", "password": "diana_hero", "borrowed_books": []},
        ]

        for user in initial_users:
            borrow_records = []
            for isbn in user["borrowed_books"]:
                book = self.find_book_by_isbn(isbn)
                if book:
                    borrow_date = datetime.datetime.now() - datetime.timedelta(days=2)
                    record = BorrowRecord(book, borrow_date=borrow_date)
                    borrow_records.append(record)
            self.user_list.append(User(user["name"], user["user_id"], user["password"], borrow_records))

    def add_book(self, title, author, genre, isbn):
        if self.find_book_by_isbn(isbn):
            print(f"Error: A book with ISBN {isbn} already exists.")
            return
        new_book = Book(title, author, genre, isbn)
        self.book_list.append(new_book)
        print(f"Book '{title}' added successfully.")

    def search_books(self, **kwargs):
        results = self.book_list
        for key, value in kwargs.items():
            if key not in ["title", "author", "genre", "isbn"]:
                continue
            results = [book for book in results if getattr(book, key).lower() == value.lower()]
        return results

    def display_available_books(self):
        available = [book for book in self.book_list if book.is_available()]
        if not available:
            print("No available books at the moment.")
            return
        for book in available:
            print(f"Title: {book.title}, Author: {book.author}, Genre: {book.genre}, ISBN: {book.isbn}, Avg Rating: {book.average_rating:.2f}")

    def issue_book(self, user_id, isbn):
        transaction = Transaction(self)
        transaction.issue(user_id, isbn)

    def return_book(self, user_id, isbn):
        transaction = Transaction(self)
        transaction.return_book(user_id, isbn)

    def rate_book(self, user_id, isbn, rating):
        user = self.find_user_by_id(user_id)
        if not user:
            print("Error: User ID not found.")
            return

        # Check if user has borrowed the book > 1 day
        if not user.has_borrowed_book_before(isbn):
            print("Error: You can only rate books you have borrowed for more than one day.")
            return

        book = self.find_book_by_isbn(isbn)
        if not book:
            print("Error: Book ISBN not found.")
            return

        try:
            rating_value = int(rating)
            if not (1 <= rating_value <= 5):
                raise ValueError("Error: Your rating must be an integer between 1 and 5.")
            book.add_rating(rating_value)
            print(f"Thank you! You rated '{book.title}' with a {rating_value}.")
        except ValueError as e:
            print(e)

    def display_average_ratings(self):
        for book in self.book_list:
            print(f"Title: {book.title}, Average Rating: {book.average_rating:.2f}")

    def find_book_by_isbn(self, isbn):
        for book in self.book_list:
            if book.isbn == isbn:
                return book
        return None

    def find_user_by_id(self, user_id):
        for user in self.user_list:
            if user.user_id == user_id:
                return user
        return None

    def validate_user_input(self, prompt):
        user_input = input(prompt).strip()
        if not user_input:
            print("Error: Input cannot be empty. Please try again.")
            return None
        return user_input

    def user_menu(self):
        while True:
            print("\n--- Library Management System ---")
            print("1. Display Available Books")
            print("2. Search Books")
            print("3. Issue Book")
            print("4. Return Book")
            print("5. Rate Book")
            print("6. Display Average Ratings")
            print("7. Exit")
            choice = self.validate_user_input("Enter your choice (1-7): ")

            if choice == "1":
                self.display_available_books()
            elif choice == "2":
                criterion = self.validate_user_input("Search by title, author, genre, or ISBN? ").lower()
                if criterion not in ["title", "author", "genre", "isbn"]:
                    print("Invalid search criterion.")
                    continue
                value = self.validate_user_input(f"Enter the {criterion}: ")
                if value is None:
                    continue
                results = self.search_books(**{criterion: value})
                if results:
                    for book in results:
                        status = "Issued" if not book.is_available() else "Available"
                        print(f"Title: {book.title}, Author: {book.author}, Genre: {book.genre}, ISBN: {book.isbn}, Status: {status}, Avg Rating: {book.average_rating:.2f}")
                else:
                    print("No books found matching the criteria.")
            elif choice == "3":
                user_id = self.validate_user_input("Enter your User ID: ")
                isbn = self.validate_user_input("Enter the ISBN of the book to issue: ")
                if user_id and isbn:  # ensure both inputs are provided
                    self.issue_book(user_id, isbn)
            elif choice == "4":
                user_id = self.validate_user_input("Enter your User ID: ")
                isbn = self.validate_user_input("Enter the ISBN of the book to return: ")
                if user_id and isbn:
                    self.return_book(user_id, isbn)
            elif choice == "5":
                user_id = self.validate_user_input("Enter your User ID: ")
                isbn = self.validate_user_input("Enter the ISBN of the book to rate: ")
                if user_id and isbn:
                    rating = self.validate_user_input("Enter your rating (1-5): ")
                    self.rate_book(user_id, isbn, rating)
            elif choice == "6":
                self.display_average_ratings()
            elif choice == "7":
                print("Exiting the program. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    library_system = LibrarySystem()
    library_system.user_menu()


