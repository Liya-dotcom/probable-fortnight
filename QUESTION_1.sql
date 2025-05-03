--  QUESTION 1

-- Create a Database of a Library Management System
CRAETE DATABASE LibrarySystem;
USE LibrarySystem;

--  Create a Table for storing loan information
-- This table will track which books are loaned out, to whom, and the dates of the loans
CREATE TABLE Loans (
    LoanID INT PRIMARY KEY AUTO_INCREMENT,
    BookID INT NOT NULL,
    MemberID INT NOT NULL,
    LoanDate DATE DEFAULT CURRENT_DATE,
    ReturnDate DATE,
    FOREIGN KEY (BookID) REFERENCES Books(BookID),
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID)
);

-- Create a table for Reservations
-- This table will track which books are reserved, by whom, and the dates of the reservations
CREATE TABLE Reservations (
    ReservationID INT PRIMARY KEY AUTO_INCREMENT,
    BookID INT NOT NULL,
    MemberID INT NOT NULL,
    ReservationDate DATE DEFAULT CURRENT_DATE,
    ExpirationDate DATE,
    FOREIGN KEY (BookID) REFERENCES Books(BookID),
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID)
);


-- Create a table for storing book information
-- This table will store details about each book in the library
CREATE TABLE Books (
    BookID INT PRIMARY KEY AUTO_INCREMENT,
    Title VARCHAR(255) NOT NULL,
    Author VARCHAR(255) NOT NULL,
    Genre VARCHAR(100),
    Published_Year INT,
    ISBN VARCHAR(20) UNIQUE NOT NULL
);


-- Create a table for storing member information
-- This table will store details about each member of the library
CREATE TABLE Members (
    MemberID INT PRIMARY KEY AUTO_INCREMENT,
    FirstName VARCHAR(100) NOT NULL,
    LastName VARCHAR(100) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    PhoneNumber VARCHAR(20),
    JoinDate DATE DEFAULT CURRENT_DATE
);



-- Insert data to the Books table

INSERT INTO Books (Title, Author, Genre, Published_Year, ISBN)
VALUES 
('The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', 1925, '9780743273565'),
('To Kill a Mockingbird', 'Harper Lee', 'Fiction', 1960, '9780061120084'),
('1984', 'George Orwell', 'Dystopian', 1949, '9780451524935'),
('Countdown to Zero Day_ Stuxnet and the Launch of the Worlds First Digital Weapon', 'Kim Zetter', 'Technology', 2014, '9780770436179'),
('Notpetya', 'The Most Devastating Cyberattack in History', 'Andy Greenberg', 'Technology', 2018, '9785445666866'),
('The Flash', 'The Flash_ Rebirth', 'Comic', 2009, '9781401221954');

INSERT INTO Members (FirstName, LastName, Email, PhoneNumber)
VALUES
('Liyabona', 'Thebe', 'liyabona.thebe@gmail.com', 0810882834),
('John', 'Doe', 'johndoe@example.com', 0798765432),
('Vuyo', 'Beke', 'vuyobeke@gmail.com', 0712345678),
('Thandi', 'Moyo', 'thandi.moyo@vs.com', 0823456789),
('Sipho', 'Nkosi', 'siphi.nkosi@vs.com', 0834567890),
('Nandi', 'Dlamini', 'nandi.dlamini@vd.com', 0954621213);


-- Insert data to the Loans table
INSERT INTO Loans (BookID, MemberID, LoanDate, ReturnDate)
VALUES
(1, 1, '2023-10-01', NULL),
(2, 2, '2023-10-02', '2023-10-15'),
(3, 3, '2023-10-03', NULL),
(4, 4, '2023-10-04', '2023-10-20'),
(5, 5, '2023-10-05', NULL),
(6, 6, '2023-10-06', '2023-10-25');


-- Insert data to the Reservations table
INSERT INTO Reservations (BookID, MemberID, ReservationDate, ExpirationDate)
VALUES
(1, 2, '2023-10-01', '2023-10-15'),
(2, 3, '2023-10-02', '2023-10-20'),
(3, 4, '2023-10-03', '2023-10-25'),
(4, 5, '2023-10-04', '2023-11-01'),
(5, 6, '2023-10-05', '2023-11-05'),
(6, 1, '2023-10-06', '2023-11-10');

-- Query to get all books currently on loan
SELECT b.Title, m.FirstName, m.LastName, l.LoanDate, l.ReturnDate
FROM Loans l
JOIN Books b ON l.BookID = b.BookID 
JOIN Members m ON l.MemberID = m.MemberID
WHERE l.ReturnDate IS NULL;


-- Query to get all reservations that are about to expire
SELECT b.Title, m.FirstName, m.LastName, r.ReservationDate, r.ExpirationDate    
FROM Reservations r
JOIN Books b ON r.BookID = b.BookID
JOIN Members m ON r.MemberID = m.MemberID
WHERE r.ExpirationDate < CURRENT_DATE + INTERVAL 7 DAY;


