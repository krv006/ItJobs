CREATE TABLE Glassdoor (
    Job_id INT IDENTITY(1,1) PRIMARY KEY,
    title VARCHAR(255),
    company VARCHAR(255),
    location VARCHAR(MAX),
    location_sub VARCHAR(MAX),
    title_sub VARCHAR(MAX),
    skills VARCHAR(MAX),
    salary VARCHAR(MAX),
    [date] DATE,
    CONSTRAINT UQ_Title_Company_Date UNIQUE (title, company)
);

go

select * from Glassdoor
