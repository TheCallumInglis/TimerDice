CREATE TABLE "user" (
    userid SERIAL PRIMARY KEY,
    organisation int NOT NULL, -- FK Organisation.OrganisationID
    "name" text NOT NULL
);

CREATE TABLE apikey (
    apikeyid SERIAL PRIMARY KEY,
    apikey char(36) NOT NULL,
    "user" int NOT NULL -- FK User.UserID
);

CREATE TABLE organisation (
    organisationid SERIAL PRIMARY KEY,
    "name" text NOT NULL
);

CREATE TABLE dice (
    diceid SERIAL PRIMARY KEY,
    uuid char(18) NOT NULL,
    "name" text NOT NULL,
    faces int NOT NULL
);

CREATE TABLE diceface (
    dicefaceid SERIAL PRIMARY KEY,
    dice int NOT NULL, -- FK Dice.DiceID
    facenumber int NOT NULL
);

CREATE TABLE tasks (
    taskid SERIAL PRIMARY KEY,
    tasktype int NOT NULL, -- FK TaskType.TaskTypeID
    organisation int NOT NULL, -- FK Organisation.OrganisationID
    "name" text NOT NULL,
    external_task_id text NULL
);

CREATE TABLE tasktype (
    tasktypeid SERIAL PRIMARY KEY,
    "name" text NOT NULL,
    jsonconfig text NULL
);

CREATE TABLE recording (
    recordingID SERIAL PRIMARY KEY,
    dice int NOT NULL, -- FK Dice.DiceID
    task int NOT NULL, -- FK Task.TaskID
    "user" int NOT NULL, -- FK Task.UserID
    starttime timestamp NOT NULL,
    endtime timestamp NULL
);

CREATE TABLE userdice (
    userdiceid SERIAL PRIMARY KEY,
    "user" int NOT NULL, -- FK User.UserID
    dice int NOT NULL -- FK Dice.DiceID
);

CREATE TABLE dicefacetask (
    dicefacetaskid SERIAL PRIMARY KEY,
    diceface int NOT NULL, -- FK DiceFace.DiceFaceID
    task int NOT NULL -- FK Tasks.TaskID
);

CREATE TABLE integration (
    integrationid SERIAL PRIMARY KEY,
    integration text NOT NULL,
    presetjson text NOT NULL
);

-- Add Constraints
-- ALTER TABLE [User]
--     ADD CONSTRAINT FK_User_Organisation FOREIGN KEY (Organisation)
--         REFERENCES Organisation(OrganisationID)
--         ON DELETE CASCADE
--         ON UPDATE CASCADE;

-- ALTER TABLE [APIKEY]
--     ADD CONSTRAINT FK_APIKEY_USER FOREIGN KEY ([User])
--         REFERENCES [User](UserID)
--         ON DELETE CASCADE
--         ON UPDATE CASCADE;

-- ALTER TABLE [APIKEY]
--   ADD CONSTRAINT UQ_APIKEY_KEY UNIQUE (APIKEY)

-- ALTER TABLE [Dice]
--   ADD CONSTRAINT UQ_Dice_UUID UNIQUE (UUID)

-- ALTER TABLE DiceFace
--     ADD CONSTRAINT FK_DiceFace_Dice FOREIGN KEY (Dice)
--         REFERENCES Dice(DiceID)
--         ON DELETE CASCADE
--         ON UPDATE CASCADE;

-- ALTER TABLE Tasks
--     ADD CONSTRAINT FK_Tasks_TaskType FOREIGN KEY (TaskType)
--         REFERENCES TaskType(TaskTypeID)
--         ON DELETE CASCADE
--         ON UPDATE CASCADE;

-- ALTER TABLE Tasks
--     ADD CONSTRAINT FK_Tasks_Organisation FOREIGN KEY (Organisation)
--         REFERENCES Organisation(OrganisationID)
--         ON DELETE CASCADE
--         ON UPDATE CASCADE;

-- ALTER TABLE Recording
--     ADD CONSTRAINT FK_Recording_Dice FOREIGN KEY (Dice)
--         REFERENCES Dice(DiceID)
--         ON DELETE CASCADE
--         ON UPDATE CASCADE;

-- ALTER TABLE Recording
--     ADD CONSTRAINT FK_Recording_Tasks FOREIGN KEY (Task)
--         REFERENCES Tasks(TaskID)
--         ON DELETE CASCADE
--         ON UPDATE CASCADE;

-- /**
-- ALTER TABLE Recording
--     ADD CONSTRAINT FK_Recording_User FOREIGN KEY ([User])
--         REFERENCES [User](UserID)
--         ON DELETE CASCADE
--         ON UPDATE CASCADE;
-- **/

-- ALTER TABLE UserDice
--     ADD CONSTRAINT FK_UserDice_User FOREIGN KEY ([User])
--         REFERENCES [User](UserID)
--         ON DELETE CASCADE
--         ON UPDATE CASCADE;

-- ALTER TABLE UserDice
--     ADD CONSTRAINT FK_UserDice_Dice FOREIGN KEY (Dice)
--         REFERENCES Dice(DiceID)
--         ON DELETE CASCADE
--         ON UPDATE CASCADE;

-- ALTER TABLE DiceFaceTask
--     ADD CONSTRAINT FK_DiceFaceTask_DiceFace FOREIGN KEY (DiceFace)
--         REFERENCES DiceFace(DiceFaceID)
--         ON DELETE CASCADE
--         ON UPDATE CASCADE;

-- ALTER TABLE DiceFaceTask
--     ADD CONSTRAINT FK_DiceFaceTask_Task FOREIGN KEY (Task)
--         REFERENCES Tasks(TaskID)
--         ON DELETE CASCADE
--         ON UPDATE CASCADE;