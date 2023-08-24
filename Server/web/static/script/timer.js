const Timer = {
    activeNavMenuCls: 'link-secondary',

    // Highlight the currently active nav menu item, init JS vars for section
    setNavMenu: () => {
        "use strict";
        let path = window.location.pathname;

        document.querySelectorAll('[href="' + path + '"]').forEach(el => { 
            el.classList.add(Timer.activeNavMenuCls); 
        });

        Timer.setupGlobalJS();

        switch (path) {
            case '/dice':
                Timer.setupDiceJS();
                break

            case '/tasks':
                Timer.setupTasksJS();
                break
        }
    },

    setupGlobalJS: () => {
        Timer.lblTaskSpendTitle = document.getElementById('lblTaskSpendTitle');
        Timer.taskSpendTable = document.getElementById('taskSpendTable');
        Timer.lblTaskSpendError = document.getElementById('lblTaskSpendError');
        Timer.taskSpendModal = new bootstrap.Modal(document.getElementById('taskSpendModal'));
    },

    /** DICE **/
    setupDiceJS: () => {
        // Add Dice Config
        Timer.frmAddDice = document.getElementById('frmAddDice');
        Timer.addDiceModal = new bootstrap.Modal(document.getElementById('addDiceModal'));
        Timer.lblAddDiceError = document.getElementById('lblAddDiceError');
        Timer.btnAddNewDice = document.getElementById('btnAddNewDice');
        Timer.btnRefreshDiceTable = document.getElementById('btnRefreshDiceTable');
        Timer.diceTable = document.getElementById('diceTable');

        // Dice Face Config
        Timer.diceFaceModal = new bootstrap.Modal(document.getElementById('diceFaceModal'));
        Timer.lblDiceFaceModalUUID = document.getElementById('lblDiceFaceModalUUID');
        Timer.lblDiceFaceModalError;
        Timer.diceFaceTable = document.getElementById('diceFaceTable');

        // Assign task to dice face
        Timer.assignTaskToDiceFaceModal = new bootstrap.Modal(document.getElementById('assignTaskToDiceFaceModal'));
        Timer.frmAssignTaskToDiceFace = document.getElementById('frmAssignTaskToDiceFace');
        Timer.optDiceFaceTaskList = document.getElementById('dicefacetasktasklist');
        Timer.lblAssignTaskToDiceFaceError = document.getElementById('lblAssignTaskToDiceFaceError');

        Timer.frmAddDice.addEventListener("submit", (e) => {
            e.preventDefault();
            Timer.addNewDice();
        });
        
        Timer.btnRefreshDiceTable.addEventListener('click', (e) => {
            e.preventDefault();
            Timer.refreshDiceTable();
        });
        
        Timer.btnAddNewDice.addEventListener('click', (e) => {
            e.preventDefault();
        
            Timer.ResetNewDiceModal();
            Timer.addDiceModal.show();
        });
        
        Timer.frmAssignTaskToDiceFace.addEventListener("submit", (e) => {
            e.preventDefault();
            Timer.AssignTaskToDiceFace();
        });
    },

    addNewDice: async () => {
        "use strict";

        Timer.lblAddDiceError.classList.add('hidden');

        try {
            let response = await fetch(
                "/api/dice", 
                {
                    method: 'POST',
                    body: new FormData(document.querySelector('#frmAddDice')),
                }
            );

            if (response.status != 200) {
                throw 'Bad Response, got: ' + response.status + '. Error: ' + await response.text();
            }

            const result = await response.json();

            Timer.addDiceModal.hide();
            Timer.refreshDiceTable();
            appendAlert('Dice Added!', 'success', 2500);

        } catch (error) {
            Timer.lblAddDiceError.classList.remove('hidden');
            Timer.lblAddDiceError.innerText = 'Failed to add dice... ' + error;
        }
    },

    refreshDiceTable: async () => {
        "use strict";

        try {
            let response = await fetch("/api/dice");
            let result = await response.json();

            Timer.diceTable.innerHTML = "";
            for (let die in result['dice']) {
                Timer.diceTable.innerHTML += `<tr>
                    <td>${result['dice'][die]['uuid']}</td>
                    <td>${result['dice'][die]['name']}</td>
                    <td>${result['dice'][die]['faces']}</td>
                    <td>
                        <a href="#" onclick="Timer.DiceDetailModal(${result['dice'][die]['diceid']});">View</a>
                    </td>
                </tr>`;
            }

        } catch (error) {
            appendAlert('Failed to fetch dice... ' + error.message, 'warning');
            // TODO Handle an error within popup
        }
    },

    ResetNewDiceModal: () => {
        "use strict";

        Timer.lblAddDiceError.classList.add('hidden');
        frmAddDice.elements['dice-uuid'].value = '';
        frmAddDice.elements.nickname.value = '';
        frmAddDice.elements.faces.value = 6;
    },

    DiceDetailModal: async (diceid) => {
        "use strict";

        Timer.lblDiceFaceModalUUID.innerText = "";
        Timer.diceFaceTable.innerHTML = "";

        let response = await fetch("/api/dice/" + diceid);
        let result = await response.json();

        if (result['dice']) {
            Timer.lblDiceFaceModalUUID.innerText = result['dice']['uuid'];
        }

        for (let face in result['faces']) {
            let assignTaskLink = (result['faces'][face]['taskname'] == null) ? 'Assign Task' : 'Change';

            let clearTaskLink = (result['faces'][face]['taskname'] == null) 
                ? '' 
                : `| <a href="#" onclick="Timer.ClearDiceFaceTask(${result['faces'][face]['diceid']}, ${result['faces'][face]['facenumber']});">Clear</a>`;

            Timer.diceFaceTable.innerHTML += `<tr>
                <td>${result['faces'][face]['facenumber']}</td>
                <td>
                    ${result['faces'][face]['taskname'] == null 
                        ? '-'
                        : `<a href="#" onclick="Timer.taskSpendReport(${result['faces'][face]['taskid']});">${result['faces'][face]['taskname']}</a>`
                    }
                </td>
                <td>
                    <a href="#" onclick="Timer.AssignTaskToDiceFaceModal(
                        ${result['faces'][face]['diceid']},
                        '${result['faces'][face]['uuid']}',
                        ${result['faces'][face]['facenumber']}
                    );">${assignTaskLink}</a>

                    ${clearTaskLink}
                </td>
            </tr>`;
        }

        Timer.diceFaceModal.show();
    },

    AssignTaskToDiceFaceModal: async (diceid, diceuuid, facenumber) => {
        "use strict";

        Timer.diceFaceModal.hide();

        // Reset Elements
        Timer.lblAssignTaskToDiceFaceError.classList.add('hidden');
        frmAssignTaskToDiceFace.elements.dicefacetaskdiceid.value = diceid;
        frmAssignTaskToDiceFace.elements.dicefacetaskuuid.value = diceuuid;
        frmAssignTaskToDiceFace.elements.dicefacetaskface.value = facenumber;
        frmAssignTaskToDiceFace.elements.dicefacetasktasklist.value = null;
        Timer.optDiceFaceTaskList.innerHTML = ""; // Clear Dropdown

        Timer.assignTaskToDiceFaceModal.show();

        // Get Possible Tasks (Not already assigned to this dice)
        let response = await fetch("/api/tasks/available/" + diceid);
        let result = await response.json();

        if (result['tasks'].length == 0) {
            Timer.lblAssignTaskToDiceFaceError.classList.remove('hidden');
            Timer.lblAssignTaskToDiceFaceError.innerText = 'No more tasks available to assign';
            return;
        }

        AddOptionToSelect(Timer.optDiceFaceTaskList, 'Select...', null, true, true);
        for (let task in result['tasks']) {
            AddOptionToSelect(
                Timer.optDiceFaceTaskList, 
                result['tasks'][task]['name'],
                result['tasks'][task]['taskid']
            );
        }
    },

    AssignTaskToDiceFace: async () => {
        "use strict";

        Timer.lblAssignTaskToDiceFaceError.classList.add('hidden');

        try {
            let response = await fetch(
                "/api/tasks/assign", 
                {
                    method: 'POST',
                    body: new FormData(document.querySelector('#frmAssignTaskToDiceFace')),
                }
            );

            if (response.status != 200) {
                throw 'Bad Response, got: ' + response.status + '. Error: ' + await response.text();
            }

            const result = await response.json();

            Timer.assignTaskToDiceFaceModal.hide();
            await Timer.DiceDetailModal(document.getElementById('dicefacetaskdiceid').value);
            // TODO Alert this worked!

        } catch (error) {
            Timer.lblAssignTaskToDiceFaceError.classList.remove('hidden');
            Timer.lblAssignTaskToDiceFaceError.innerText = 'Failed to assign task... ' + error;
        }
    },

    ClearDiceFaceTask: async (diceid, facenumber) => {
        "use strict";

        try {
            let response = await fetch(
                "/api/tasks/assign", 
                {
                    method: 'DELETE',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        'diceid' : diceid,
                        'facenumber' : facenumber
                    }),
                }
            );

            if (response.status != 200) {
                throw 'Bad Response, got: ' + response.status + '. Error: ' + await response.text();
            }

            await Timer.DiceDetailModal(diceid);

        } catch (error) {
            alert("BOOO");
        }
    },
    /** END DICE **/

    /** TASK **/
    setupTasksJS: () => {
        "use strict";

        /** TASKS **/
        // Add Task Config
        Timer.btnAddNewTask = document.getElementById('btnAddNewTask');
        Timer.btnRefreshTaskTable = document.getElementById('btnRefreshTaskTable');
        Timer.taskTable = document.getElementById('taskTable');

        // Add Task Modal
        Timer.frmAddTask = document.getElementById('frmAddTask');
        Timer.addTaskModal = new bootstrap.Modal(document.getElementById('addTaskModal'));
        Timer.lblAddTaskError = document.getElementById('lblAddTaskError');
        Timer.txtAddTaskName = document.getElementById('addTaskName');
        Timer.optAddTaskType = document.getElementById('addTaskType');
        Timer.spinAddTaskExternalID = document.getElementById('spinAddTaskExternalID');
        Timer.btnAddTaskExternalID = document.getElementById('btnAddTaskExternalID');
        Timer.addTaskExternalIDManual = document.getElementById('addTaskExternalIDManual');
        Timer.optAddTaskExternalID = document.getElementById('addTaskExternalID');
        Timer.optAddTaskOrganisation = document.getElementById('addTaskOrganisation');

        // Add Task Type Modal
        Timer.txtAddTaskTypeJsonConfig = document.getElementById('addTaskTypeJsonConfig');

        Timer.frmAddTask.addEventListener("submit", (e) => {
            e.preventDefault();
            Timer.addNewTask();
        });

        Timer.addTaskExternalIDManual.addEventListener("blur", async (e) => {
            e.preventDefault();
            Timer.LookupExternalTask();
        });

        Timer.optAddTaskType.addEventListener("change", async (e) => {
            e.preventDefault();
            
            // Check if task type requires an external task ID to function

           // Loading Icon
           Timer.spinAddTaskExternalID.classList.remove("hidden");

           let request = await fetch("/api/tasktypes/" + Timer.optAddTaskType.value);
           let result = await request.json();

            if (!result.hasOwnProperty("tasktype") || 
                !result["tasktype"].hasOwnProperty("hasexternalconfig") || 
                !result["tasktype"]["hasexternalconfig"]
            ) {
                console.log("External Task ID Not Required");

                // Disable, Clear & Hide Manual Task ID Entry
                Timer.addTaskExternalIDManual.disabled = true;
                Timer.addTaskExternalIDManual.required = false;
                Timer.addTaskExternalIDManual.classList.add("hidden");

                // Disable & Clear Dropdown
                Timer.optAddTaskExternalID.disabled = true;
                Timer.optAddTaskExternalID.required = false;
                Timer.optAddTaskExternalID.classList.remove("hidden");
                ClearSelect(Timer.optAddTaskExternalID);

                // Hide Quick Links button
                Timer.btnAddTaskExternalID.classList.add("hidden");
                
            } else {
                // Show Quick Links button & refresh external tasks list
                Timer.btnAddTaskExternalID.classList.remove("hidden");
                Timer.QuickLinkExternalTask();
                return;
            }

            // Loading Icon
            Timer.spinAddTaskExternalID.classList.add("hidden");
        });
        
        Timer.btnAddNewTask.addEventListener('click', (e) => {
            e.preventDefault();
            Timer.ResetNewTaskModal();
            Timer.addTaskModal.show();
        });

        /** TASK TYPES **/
        // Add Task Type Config
        Timer.btnAddNewTaskType = document.getElementById('btnAddNewTaskType');
        Timer.tasktypeTable = document.getElementById('tasktypeTable');

        // Add Task Types Modal
        Timer.frmAddTaskType = document.getElementById('frmAddTaskType');
        Timer.addTaskTypeModal = new bootstrap.Modal(document.getElementById('addTaskTypeModal'));
        Timer.lblAddTaskTypeError = document.getElementById('lblAddTaskTypeError');
        Timer.txtAddTaskTypeName = document.getElementById('addTaskTypeName');

        Timer.btnAddNewTaskType.addEventListener('click', (e) => {
            e.preventDefault();
            Timer.ResetNewTaskTypeModal();
            Timer.addTaskTypeModal.show();
        });

        Timer.frmAddTaskType.addEventListener("submit", (e) => {
            e.preventDefault();
            Timer.addNewTaskType();
        });

        /** GENERIC **/
        Timer.btnRefreshTaskTable.addEventListener('click', (e) => {
            e.preventDefault();
            Timer.refreshTaskTable();
            Timer.refreshTaskTypesTable();
        });
    },

    ResetNewTaskModal: async () => {
        "use strict";

        Timer.lblAddTaskError.classList.add('hidden');
        frmAddTask.elements.addTaskName.value = "";
        frmAddTask.elements.addTaskType.innerHTML = "";
        Timer.btnAddTaskExternalID.classList.add('hidden');

        frmAddTask.elements.addTaskExternalID.disabled = true;
        frmAddTask.elements.addTaskExternalID.required = false;
        ClearSelect(Timer.optAddTaskExternalID);

        // Disable & Hide Manual Task ID Field
        Timer.addTaskExternalIDManual.value = "";
        Timer.addTaskExternalIDManual.disabled = true;
        Timer.addTaskExternalIDManual.required = false;
        Timer.addTaskExternalIDManual.classList.add("hidden");
        
        frmAddTask.elements.addTaskOrganisation.innerHTML = "";

        // Fill Drop-down options : Task Type
        let response = await fetch("/api/tasktypes");
        let result = await response.json();

        if (result['tasktypes'].length == 0) {
            Timer.lblAddTaskError.classList.remove('hidden');
            Timer.lblAddTaskError.innerText = 'No Task Types Available';
            return;
        }

        AddOptionToSelect(Timer.optAddTaskType, 'Select...', null, true, true);
        for (let tasktype in result['tasktypes']) {
            AddOptionToSelect(
                Timer.optAddTaskType, 
                result['tasktypes'][tasktype]['name'],
                result['tasktypes'][tasktype]['tasktypeid']
            );
        }

        // Fill Drop-down options: Organisation
        response = await fetch("/api/organisation");
        result = await response.json();

        if (result['organisation'].length == 0) {
            Timer.lblAddTaskError.classList.remove('hidden');
            Timer.lblAddTaskError.innerText = 'No Organisations Available';
            return;
        }

        AddOptionToSelect(Timer.optAddTaskOrganisation, 'Select...', null, true, true);
        for (let organisation in result['organisation']) {
            AddOptionToSelect(
                Timer.optAddTaskOrganisation, 
                result['organisation'][organisation]['name'],
                result['organisation'][organisation]['organisationid']
            );
        }
    },

    addNewTask: async () => {
        "use strict";

        Timer.lblAddTaskError.classList.add('hidden');

        // Check Task Name, Type & Org Selected
        let errors = [];
        if (Timer.txtAddTaskName.value == "") {
            errors.push("Task Name Missing");
        }
        if (Timer.optAddTaskType.value == "null" || Timer.optAddTaskType.value == "") {
            errors.push("Task Type Missing");
        }
        if (Timer.optAddTaskOrganisation.value == "null" || Timer.optAddTaskOrganisation.value == "") {
            errors.push("Organisation Missing");
        }
        if (errors.length > 0) {
            Timer.lblAddTaskError.classList.remove("hidden");
            Timer.lblAddTaskError.innerText = "Errors Encountered: " + errors.join(", ");
            return;
        }

        try {
            let response = await fetch(
                "/api/tasks", 
                {
                    method: 'POST',
                    body: new FormData(document.querySelector('#frmAddTask')),
                }
            );

            if (response.status != 200) {
                throw 'Bad Response, got: ' + response.status + '. Error: ' + await response.text();
            }

            const result = await response.json();

            Timer.refreshTaskTable();
            appendAlert('Task Added!', 'success', 2500);
            Timer.addTaskModal.hide();

        } catch (error) {
            Timer.lblAddTaskError.classList.remove('hidden');
            Timer.lblAddTaskError.innerText = 'Failed to add task... ' + error;
        }
    },

    refreshTaskTable: async () => {
        "use strict";

        try {
            let response = await fetch("/api/tasks");
            let result = await response.json();

            Timer.taskTable.innerHTML = "";
            for (let task in result['tasks']) {
                Timer.taskTable.innerHTML += `<tr>
                    <td>${result['tasks'][task]['taskname']}</td>
                    <td>${result['tasks'][task]['tasktype']}</td>
                    <td class="text-center">${result['tasks'][task]['external_task_id'] || ""}</td>
                    <td>${result['tasks'][task]['organisation']}</td>
                    <td>
                        <a href="#" onclick="Timer.taskSpendReport(${result['tasks'][task]['taskid']});">Spend</a>
                    </td>
                </tr>`;
            }

        } catch (error) {
            appendAlert('Failed to fetch tasks... ' + error.message, 'warning');
        }
    },

    QuickLinkExternalTask: async() => {
        "use strict";

        // Loading Icon
        Timer.spinAddTaskExternalID.classList.remove("hidden");

        Timer.lblAddTaskError.innerText = "";
        Timer.lblAddTaskError.classList.add("hidden");

        ClearSelect(Timer.optAddTaskExternalID);

        let request = await fetch("/api/tasktypes/externaltasks/" + Timer.optAddTaskType.value);
        let result = await request.json();

        if (result.length == 0) {
            // Disable & Hide External Task ID Dropdown
            Timer.optAddTaskExternalID.disabled = true;
            Timer.optAddTaskExternalID.required = false;
            Timer.optAddTaskExternalID.classList.add("hidden");

            // Require & Show Manual Task ID Field
            Timer.addTaskExternalIDManual.disabled = false;
            Timer.addTaskExternalIDManual.required = true;
            Timer.addTaskExternalIDManual.classList.remove("hidden");

            Timer.lblAddTaskError.innerText = "No External Tasks Found - Add Manually";
            Timer.lblAddTaskError.classList.remove("hidden");
            return;
        }
        
        result.forEach(task => {
            AddOptionToSelect(
                Timer.optAddTaskExternalID, 
                `#${task['external_task_id']}: ${task['name']}`,
                task['external_task_id'],
                false,
                false
            );
        }); 

        // Require & Show External Task ID Dropdown
        Timer.optAddTaskExternalID.disabled = false;
        Timer.optAddTaskExternalID.required = true;
        Timer.optAddTaskExternalID.classList.remove("hidden");

        // Disable & Hide Manual Task ID Field
        Timer.addTaskExternalIDManual.disabled = true;
        Timer.addTaskExternalIDManual.required = false;
        Timer.addTaskExternalIDManual.classList.add("hidden");

        // Loading Icon
        Timer.spinAddTaskExternalID.classList.add("hidden");
    },

    LookupExternalTask: async () => {
        "use strict";

        let response = await fetch(
            `/api/tasktypes/externaltasks/${Timer.optAddTaskType.value}/${Timer.addTaskExternalIDManual.value}`
        );

        if (response.status !== 200) {
            frmAddTask.elements.addTaskName.value = "";

            Timer.spinAddTaskExternalID.classList.remove("hidden");
            Timer.lblAddTaskError.innerText = "Task Lookup By ID Failed";
            Timer.lblAddTaskError.classList.remove("hidden");
            return;
        }

        let jsonResponse = await response.json();

        // Push into view
        frmAddTask.elements.addTaskName.value = jsonResponse['name'];

        Timer.spinAddTaskExternalID.classList.add("hidden");
        Timer.lblAddTaskError.innerText = "";
        Timer.lblAddTaskError.classList.add("hidden");
    },

    // Task Type
    ResetNewTaskTypeModal: () => {
        "use strict";
        Timer.lblAddTaskTypeError.classList.add('hidden');
        frmAddTaskType.elements.addTaskTypeName.value = '';
        frmAddTaskType.elements.addTaskTypeJsonConfig.value = '';
    },

    addNewTaskType: async () => {
        "use strict";

        Timer.lblAddTaskTypeError.classList.add('hidden');

        try {
            let response = await fetch(
                "/api/tasktypes", 
                {
                    method: 'POST',
                    body: new FormData(document.querySelector('#frmAddTaskType')),
                }
            );

            if (response.status != 200) {
                throw 'Bad Response, got: ' + response.status + '. Error: ' + await response.text();
            }

            const result = await response.json();

            Timer.refreshTaskTypesTable();
            appendAlert('Task Type Added!', 'success', 2500);
            Timer.addTaskTypeModal.hide();

        } catch (error) {
            Timer.lblAddTaskTypeError.classList.remove('hidden');
            Timer.lblAddTaskTypeError.innerText = 'Failed to add task type... ' + error;
        }
    },

    PreloadIntegrationJsonConfig: async (integrationid) => {
        "use strict";

        let response = await fetch("/api/integrations/" + integrationid);
        let result = await response.json();

        if (!result.hasOwnProperty("integration") || 
            !result["integration"].hasOwnProperty("presetjson") || 
            !result["integration"]["presetjson"]
        ) {
            Timer.txtAddTaskTypeJsonConfig.value = "";
            
        } else {
            // pretty up the json out output
            Timer.txtAddTaskTypeJsonConfig.value = JSON.stringify(JSON.parse(result["integration"]["presetjson"]), null, 4);
        }
    },

    setupEditTaskType: async (tasktypeid) => {
        "use strict";

        Timer.ResetNewTaskTypeModal();

        // Get task type
        let response = await fetch("/api/tasktypes/" + tasktypeid + "/extended");
        let result = await response.json();

        if (!result.hasOwnProperty("tasktype") ||
            !result["tasktype"].hasOwnProperty("name") ||
            !result["tasktype"].hasOwnProperty("jsonconfig")
        ) {
            alert("Failed To Load Task Type! " + result); // TODO Temp
            return;
        }

        // Push into view
        // TODO TaskTypeID
        Timer.txtAddTaskTypeName.value = result["tasktype"]["name"];
        Timer.txtAddTaskTypeJsonConfig.value = JSON.stringify(JSON.parse(result["tasktype"]["jsonconfig"]), null, 4);

        // TODO Handle edits rather than creates

        Timer.addTaskTypeModal.show();
    },

    refreshTaskTypesTable: async () => {
        "use strict";

        try {
            let response = await fetch("/api/tasktypes");
            let result = await response.json();

            Timer.tasktypeTable.innerHTML = "";
            for (let tasktype in result['tasktypes']) {
                Timer.tasktypeTable.innerHTML += `<tr>
                    <td>${result['tasktypes'][tasktype]['name']}</td>
                </tr>`;
            }

        } catch (error) {
            appendAlert('Failed to fetch task types... ' + error.message, 'warning');
        }
    },
    /** END TASK **/


    /** TASK SPEND REPORT **/
    taskSpendReport: async (task_id) => {
        "use strict";

        Timer.lblTaskSpendTitle.innerText = "";
        Timer.taskSpendTable.innerHTML = "";
        Timer.lblTaskSpendError.innerText = "";

        let response = await fetch("/api/tasks/spend/" + task_id);
        let result = await response.json();

        if (result['task']) {
            Timer.lblTaskSpendTitle.innerText = result['task']['name'];
        }

        for (let recording in result['task_spend_report']) {
            Timer.taskSpendTable.innerHTML += `<tr>
                <td>${result['task_spend_report'][recording]['starttime']}</td>
                <td>${result['task_spend_report'][recording]['endtime']}</td>
                <td>${result['task_spend_report'][recording]['spendtime']}</td>
                <td>${result['task_spend_report'][recording]['username']}</td>
            </tr>`;
        }

        Timer.taskSpendModal.show();
    }
    /** END TASK SPEND REPORT **/
}

const AddOptionToSelect = (el, text, value, selected = false, disabled = false) => {
    let option = document.createElement("option");
    option.text = text;
    option.value = value;
    option.selected = selected;
    option.disabled = disabled;

    el.add(option);
}

const ClearSelect = (el) => {
    for(let i = el.options.length - 1; i >= 0; i--) {
        el.remove(i);
    }

    AddOptionToSelect(el, 'Select...', null, true, true);
}

// Alert
const appendAlert = async (message, type, duration = 0) => {
  const alertPlaceholder = document.getElementById("alertPlaceholder");
  const wrapper = document.createElement('div');

  wrapper.innerHTML = [
    `<div class="alert alert-${type} alert-dismissible" role="alert">`,
    `   <div>${message}</div>`,
    '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
    '</div>'
  ].join('');

  alertPlaceholder.append(wrapper);

  if (duration > 0) {
    await new Promise(resolve => setTimeout(resolve, duration));
    alertPlaceholder.remove(wrapper);
  }
}

Timer.setNavMenu();