CREATE TABLE [User] (
    UserID int NOT NULL PRIMARY KEY IDENTITY(1,1),
    Organisation int NOT NULL, -- FK Organisation.OrganisationID
    Name varchar(MAX) NOT NULL
)

CREATE TABLE [APIKey] (
    APIKEYID int NOT NULL PRIMARY KEY IDENTITY(1,1),
    APIKEY char(36) NOT NULL,
    [USER] int NOT NULL -- FK User.UserID
)

CREATE TABLE Organisation (
    OrganisationID int NOT NULL PRIMARY KEY IDENTITY(1,1),
    Name varchar(MAX) NOT NULL
)

CREATE TABLE Dice (
    DiceID int NOT NULL PRIMARY KEY IDENTITY(1,1),
    UUID char(18) NOT NULL,
    Name varchar(MAX) NOT NULL,
    Faces int NOT NULL
)

CREATE TABLE DiceFace (
    DiceFaceID int NOT NULL PRIMARY KEY IDENTITY(1,1),
    Dice int NOT NULL, -- FK Dice.DiceID
    FaceNumber int NOT NULL
)

CREATE TABLE Tasks (
    TaskID int NOT NULL PRIMARY KEY IDENTITY(1,1),
    TaskType int NOT NULL, -- FK TaskType.TaskTypeID
    Organisation int NOT NULL, -- FK Organisation.OrganisationID
    Name varchar(MAX) NOT NULL
)

CREATE TABLE TaskType (
    TaskTypeID int NOT NULL PRIMARY KEY IDENTITY(1,1),
    Name varchar(MAX) NOT NULL
)

CREATE TABLE Recording (
    RecordingID int NOT NULL PRIMARY KEY,
    Dice int NOT NULL, -- FK Dice.DiceID
    Task int NOT NULL, -- FK Task.TaskID
    "User" int NOT NULL, -- FK Task.UserID
    StartTime timestamp NOT NULL,
    EndTime timestamp NULL
)

CREATE TABLE UserDice (
    UserDiceID int NOT NULL PRIMARY KEY IDENTITY(1,1),
    [User] int NOT NULL, -- FK User.UserID
    Dice int NOT NULL -- FK Dice.DiceID
)

CREATE TABLE DiceFaceTask (
    DiceFaceTaskID int NOT NULL PRIMARY KEY IDENTITY(1,1),
    DiceFace int NOT NULL, -- FK DiceFace.DiceFaceID
    Task int NOT NULL -- FK Tasks.TaskID
)

-- Add Constraints
ALTER TABLE [User]
    ADD CONSTRAINT FK_User_Organisation FOREIGN KEY (Organisation)
        REFERENCES Organisation(OrganisationID)
        ON DELETE CASCADE
        ON UPDATE CASCADE;

ALTER TABLE [APIKEY]
    ADD CONSTRAINT FK_APIKEY_USER FOREIGN KEY ([User])
        REFERENCES [User](UserID)
        ON DELETE CASCADE
        ON UPDATE CASCADE;

ALTER TABLE [APIKEY]
  ADD CONSTRAINT UQ_APIKEY_KEY UNIQUE (APIKEY)

ALTER TABLE [Dice]
  ADD CONSTRAINT UQ_Dice_UUID UNIQUE (UUID)

ALTER TABLE DiceFace
    ADD CONSTRAINT FK_DiceFace_Dice FOREIGN KEY (Dice)
        REFERENCES Dice(DiceID)
        ON DELETE CASCADE
        ON UPDATE CASCADE;

ALTER TABLE Tasks
    ADD CONSTRAINT FK_Tasks_TaskType FOREIGN KEY (TaskType)
        REFERENCES TaskType(TaskTypeID)
        ON DELETE CASCADE
        ON UPDATE CASCADE;

ALTER TABLE Tasks
    ADD CONSTRAINT FK_Tasks_Organisation FOREIGN KEY (Organisation)
        REFERENCES Organisation(OrganisationID)
        ON DELETE CASCADE
        ON UPDATE CASCADE;

ALTER TABLE Recording
    ADD CONSTRAINT FK_Recording_Dice FOREIGN KEY (Dice)
        REFERENCES Dice(DiceID)
        ON DELETE CASCADE
        ON UPDATE CASCADE;

ALTER TABLE Recording
    ADD CONSTRAINT FK_Recording_Tasks FOREIGN KEY (Task)
        REFERENCES Tasks(TaskID)
        ON DELETE CASCADE
        ON UPDATE CASCADE;

/**
ALTER TABLE Recording
    ADD CONSTRAINT FK_Recording_User FOREIGN KEY ([User])
        REFERENCES [User](UserID)
        ON DELETE CASCADE
        ON UPDATE CASCADE;
**/

ALTER TABLE UserDice
    ADD CONSTRAINT FK_UserDice_User FOREIGN KEY ([User])
        REFERENCES [User](UserID)
        ON DELETE CASCADE
        ON UPDATE CASCADE;

ALTER TABLE UserDice
    ADD CONSTRAINT FK_UserDice_Dice FOREIGN KEY (Dice)
        REFERENCES Dice(DiceID)
        ON DELETE CASCADE
        ON UPDATE CASCADE;

ALTER TABLE DiceFaceTask
    ADD CONSTRAINT FK_DiceFaceTask_DiceFace FOREIGN KEY (DiceFace)
        REFERENCES DiceFace(DiceFaceID)
        ON DELETE CASCADE
        ON UPDATE CASCADE;

ALTER TABLE DiceFaceTask
    ADD CONSTRAINT FK_DiceFaceTask_Task FOREIGN KEY (Task)
        REFERENCES Tasks(TaskID)
        ON DELETE CASCADE
        ON UPDATE CASCADE;