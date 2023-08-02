CREATE OR ALTER VIEW vw_AssignedTasks
AS

SELECT
     UserDice.UserDiceID

    ,[Dice].[DiceID] AS DiceID
    ,[Dice].[UUID] AS DiceUUID
    ,[Dice].[Name] as DiceName
    ,[Dice].[Faces] As DiceFaces

    ,[User].[UserID] AS UserID
    ,[User].[Name] As UserName

    ,[Organisation].OrganisationID AS OrganisationID
    ,[Organisation].[Name] AS Organisation

    -- Faces
    ,[DiceFace].DiceFaceID
    ,[DiceFace].FaceName

    -- Tasks
    ,[Tasks].TaskID AS TaskID
    ,[Tasks].[Name] AS TaskName
    ,[TaskType].[Name] AS TaskType

FROM UserDice
    LEFT OUTER JOIN [Dice] ON UserDice.[Dice] = [Dice].DiceID
    LEFT OUTER JOIN [User] ON UserDice.[User] = [User].UserID
    LEFT OUTER JOIN [Organisation] ON [User].Organisation = [Organisation].OrganisationID
    LEFT OUTER JOIN DiceFace ON [Dice].DiceID = [DiceFace].Dice -- Faces
    LEFT OUTER JOIN DiceFaceTask ON DiceFace.DiceFaceID = DiceFaceTask.DiceFace -- Faces-to-Tasks Mapping
    LEFT OUTER JOIN Tasks ON DiceFaceTask.Task = Tasks.TaskID -- Tasks
    LEFT OUTER JOIN TaskType On Tasks.TaskType = TaskType.TaskTypeID

-- =============================================================================

CREATE VIEW TaskSpend
AS

SELECT 
     Tasks.TaskID
    ,Tasks.TaskType
    ,Tasks.Organisation
    ,Tasks.Name
    ,(
        SELECT 
            SUM(
                DATEDIFF(second, StartTime, EndTime)
            ) AS Duration 
        FROM Recording 
        WHERE Recording.Task = Tasks.TaskID
    ) AS Spend
FROM Tasks
