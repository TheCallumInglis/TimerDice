CREATE VIEW vw_assignedtasks
AS

SELECT
     userdice.userdiceid

    ,dice.diceid
    ,dice.uuid
    ,dice.name
    ,dice.faces

    ,"user".userid
    ,"user"."name" As username

    ,organisation.organisationid
    ,organisation."name" AS organisation

    -- Faces
    ,diceface.dicefaceid
    ,diceface.facenumber

    -- Tasks
    ,tasks.taskid
    ,tasks."name" AS taskname
    ,tasktype."name" AS tasktype

FROM userdice
    LEFT OUTER JOIN dice ON dice.diceid = userdice.dice
    LEFT OUTER JOIN "user" ON userdice."user" = "user".userid
    LEFT OUTER JOIN organisation ON "user".organisation = organisation.organisationid
    LEFT OUTER JOIN diceface ON dice.diceid = diceface.dice -- Faces
    LEFT OUTER JOIN dicefacetask ON diceface.dicefaceid = dicefacetask.diceface -- Faces-to-Tasks Mapping
    LEFT OUTER JOIN tasks ON dicefacetask.task = tasks.taskid -- Tasks
    LEFT OUTER JOIN tasktype On tasks.tasktype = tasktype.tasktypeid


-- =============================================================================

CREATE VIEW vw_taskspend
AS

SELECT 
     tasks.taskid
    ,tasktype."name" AS tasktype
    ,organisation."name" as organisation
    ,tasks."name"
    ,(
        SELECT 
            SUM(
                extract(EPOCH from recording.endtime::timestamp - recording.starttime::timestamp)
            ) AS duration 
        FROM recording
        WHERE recording.task = tasks.taskid
    ) AS spend

FROM tasks
    LEFT OUTER JOIN tasktype On tasks.tasktype = tasktype.tasktypeid
    LEFT OUTER JOIN organisation ON tasks.organisation = organisation.organisationid
