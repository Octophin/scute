let getSelectedDevices = function () {

    let selected = Array.from(document.querySelectorAll(".deviceHeader[data-active]"));

    return selected.map(function (element) {

        return element.getAttribute("data-device");

    });

};

document.querySelectorAll(".clickSelect").forEach(function (element) {

    let device = element.getAttribute("data-device");
    let deviceReportCells = document.querySelectorAll("tr [data-device='" + device + "']");

    element.addEventListener("click", function () {

        let isActive = element.getAttribute("data-active");

        deviceReportCells.forEach(function (tableCell) {

            if (!isActive) {

                tableCell.setAttribute("data-active", "true");

            } else {

                tableCell.removeAttribute("data-active");

            }

        });

        populateButtons();

    });

});

let populateButtons = function () {

    let selected = getSelectedDevices();

    let bulkActions = Array.from(document.querySelectorAll("[data-bulk='true']"));

    let singleActions = Array.from(document.querySelectorAll("[data-bulk='false']"));


    if (selected.length) {

        bulkActions.forEach(function (element) {

            element.removeAttribute("disabled");

        });

        if (selected.length === 1) {

            singleActions.forEach(function (element) {

                element.removeAttribute("disabled");

            });

        } else {

            singleActions.forEach(function (element) {

                if (!element.classList.contains('notHidden')) {
                    element.setAttribute("disabled", true);
                }

            });

        }

    } else {

        Array.from(document.querySelectorAll(".actions select, .actions button")).forEach(function (element) {

            if (!element.classList.contains('notHidden')) {
                element.setAttribute("disabled", true);
            }

        });


    }

};

populateButtons();

document.querySelectorAll("input, select").forEach(function (element) {

    element.addEventListener("change", function (e) {

        if (e.target.value) {

            e.target.setAttribute("data-changed", "true");

        } else {

            e.target.removeAttribute("data-changed");

        }


    });

});

let triggerAction = function (e) {

    if (!getSelectedDevices().length) {

        return false;

    }

    let element = e.currentTarget;

    if (element.hasAttribute("disabled")) {

        return false;

    }

    let value;

    // if (element.tagName.toLowerCase() === "select") {  // no longer a select..
    if (element.classList.contains('actionButton')){

        value = element.value;

        if (!value) {

            return false;

        }

    }

    let action = element.getAttribute("data-action");
    let selectedDevices = getSelectedDevices();

    let query = "";

    selectedDevices.forEach(function (device) {

        query += "devices[]=" + device + "&";

    });

    let targetURL = action + "?" + query;

    // Add value for select boxes

    if (value) {

        targetURL += "&value=" + value;

    }
    

    if (element.hasAttribute("data-popupWarning") || element.hasAttribute("data-usermessage")) {

        let devicesDisplay = selectedDevices.join(', ');

        let warning = "Run " + element.innerHTML + " for " + devicesDisplay + "?";

        let popupButtons = [];
        if(element.hasAttribute("data-popupButtons")){
            popupButtons = element.getAttribute("data-popupButtons").split('|'); 
        }

        if(element.hasAttribute("data-usermessage")){
            let message = element.getAttribute("data-usermessage");
            if (selectedDevices.length === 1){
                message = message.replace('(s)', '');
            } else {
                message = message.replace('(s)', 's');
            }
            
            warning = message + '<br />' +  devicesDisplay; 

        }

        let lockscreenData = element.getAttribute("data-lockscreen");
        let lockscreen = false;
        if (lockscreenData === "true"){
            lockscreen = true;
        }

        showConfirm(warning, targetURL, lockscreen, popupButtons);

        return false;

    } else {

        document.location.href = targetURL;

    }

};

let showConfirm = function (warning, targetURL, lockscreen=false, buttonSet=[], isForm = false) {

    
    // Remove existing popup
    if (document.getElementById("popup")) {

        document.getElementById("popup").outerHTML = "";

    }

    // button text array.  Only first and second elements are used.
    if( buttonSet === '' || buttonSet === null || buttonSet.length === 0){
        buttonSet = ["OK!", "Cancel"];
    }

    // lock the screen?
    let lockscreenJS = '';
    if (lockscreen){
        lockscreenJS = 'lockScreenOverlay(); ';
    }

    //is this a form confirm?
    let onclickProcess = `okClickProcess('${targetURL}'); `;
    if (isForm){
        onclickProcess = `document.getElementById('${isForm}').submit(); `;
    }

    let popup = `<section id="popup" class="are-you-sure">
                    <div class="pop-up navy">
                        <p>${warning}</p>
                        <div class="pop-up-buttons">
                            <button onclick="${lockscreenJS} ${onclickProcess} ">${buttonSet[0]}</button>`;
    if (buttonSet.length !== 1){
        popup += `<button onclick="document.getElementById('popup').outerHTML = ''">${buttonSet[1]}</button>`;
    }
                           
    popup += `</div>
              </div>
            </section>`;

    document.querySelector("main").insertAdjacentHTML("afterbegin", popup);

};


let showAlert = function (warning) {

    // Remove existing popup

    if (document.getElementById("popup")) {

        document.getElementById("popup").outerHTML = "";

    }

    let popup = `<section id="popup" class="are-you-sure">
                    <div class="pop-up navy">
                        <p>${warning}</p>
                        <div class="pop-up-buttons">
                            <button onclick="document.getElementById('popup').outerHTML = ''">OK</button>
                        </div>
                    </div>
                </section>`;

    document.querySelector("main").insertAdjacentHTML("afterbegin", popup);

};


let okClickProcess = function (targetURL){
    console.log(targetURL);
    // close the poptp this came from and redirect the page
    document.getElementById('popup').outerHTML = '';
    document.location.href = targetURL;

};

let uploadPreset = function () {

    document.querySelectorAll("[data-preset]").forEach(function (element) {

        element.style.display = "none";

    });

    document.querySelector("[data-preset='upload']").style.display = "block";

};

let loadPreset = function (presetID) {

    Array.from(document.querySelectorAll("[data-preset-menu]")).forEach(function (menu) {

        if (menu.getAttribute("data-preset-menu") === presetID) {

            menu.setAttribute("data-selected", "true");

        } else {

            menu.removeAttribute("data-selected");

        }

    });

    document.querySelectorAll("[data-preset]").forEach(function (element) {


        if (element.getAttribute("data-preset") === presetID) {

            element.style.display = "block";
            element.setAttribute("data-selectedForm", "true");

        } else {

            element.style.display = "none";
            element.removeAttribute("data-selectedForm");

        }

    });

};

let deletePreset = function () {

    let preset = document.querySelector("[data-preset-menu][data-selected]").getAttribute("data-preset-menu");

    if (preset) {

        showConfirm("Are you sure you want to delete " + preset + " ?", "/presets?delete=" + preset);

    }

};

function displayLoadingPopup() {
    document.getElementById("loadingPopup").style.display = "block";
    lockScreenOverlay();
}

function lockScreenOverlay() {

    document.getElementById("clickOverlay").style.display = "block";
}

let loadScript = function (script) {

    Array.from(document.querySelectorAll("[data-preset-menu]")).forEach(function (menu) {

        if (menu.getAttribute("data-preset-menu") === script) {

            menu.setAttribute("data-selected", "true");

        } else {

            menu.removeAttribute("data-selected");

        }

    });

    document.querySelectorAll("[data-preset]").forEach(function (element) {


        if (element.getAttribute("data-preset") === script) {

            element.style.display = "block";
            element.setAttribute("data-selectedForm", "true");

        } else {

            element.style.display = "none";
            element.removeAttribute("data-selectedForm");

        }

    });



};


let deleteScript = function () {

    let target = document.querySelector("[data-preset-menu][data-selected]").getAttribute("data-preset-menu");

    let targetType = document.querySelector("[data-preset-menu][data-selected]").getAttribute("data-type");

    if (targetType == "system") {

        showAlert("You can not delete pre-loaded scripts.");

    } else {
        
        if (target) {
    
            showConfirm("Are you sure you want to delete " + target + " ?", "/scripts?delete=" + target);
    
        }
    }


};





// Burger Menu

function toggleBurger() {
    document.body.toggleAttribute("data-open");
}
toggleBurger();

function formatDateTime(date) {
    var d = new Date(date),
        month = (d.getMonth() + 1).toString(),
        day = d.getDate().toString(),
        year = d.getFullYear().toString(),
        hour = d.getHours().toString(),
        minute = d.getMinutes().toString();

    return year + '-' + month.padStart(2, '0') + '-' + day.padStart(2, '0') + ' ' + hour.padStart(2, '0') + ':' + minute.padStart(2, '0');
}

function getFieldName(field){
    
    fieldName = field.id.split(".");
    return " - " + fieldName[1] + " (" + fieldName[0] + ") \n";
}

var buttonClicked; // used to flag which of 2 form button types has been clicked - CONFIG page.

function confirmSubmitConfig(theForm) {

    if (buttonClicked === "save"){
       
        changedFields = document.querySelectorAll("[data-changed]");

        if (changedFields.length == 0){

            message = 'No fields have been changed. \n\n';

        } else {
            
            message = changedFields.length + ' fields have changed. \n';

            fieldList =  Object.values(changedFields).map(getFieldName); // returns array 

            message += fieldList.join('') +  '\n\n'; // avoid the auto joining ','

        }

        message += 'Save This Config to Device "' + deviceIDString.innerText + '"?';

        showConfirm(message, '', false, ["Apply Changes","Cancel"], theForm.id );

        return false;

    } else {
        message = "Click 'OK' to transfer these config setting to the Preset Page.<br>Enter a preset name and press save on the next page.";

        alert(confirm(message));
        
        showConfirm(message, '', false, ["Save To Preset","Cancel"], theForm.id );

        return false;

            }

}

function showHideDiv(targetID) {

    let x = document.getElementById(targetID);
    if (x.style.display === "none" || x.style.display === "") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }

}


if(document.getElementById("warningFieldsChanged")){

    checkForChanges();

}

function checkForChanges(){
    changedFields = document.querySelectorAll("[data-changed]");
    let x = document.getElementById('warningFieldsChanged');
    if (changedFields.length != 0){
        x.style.display = "block";
        
    } else {
        x.style.display = "none";

    }
    setTimeout(checkForChanges, 1000);
}

function checkPresetName(){

    // which preset div is selected?

    presetName = document.querySelectorAll("[data-selectedForm]")[0].getElementsByTagName("input")[0].value.trim();

    if (presetName === ''){
                showAlert("Preset Name can not be blank");
        return false;
    }


    let existing = document.getElementsByClassName("preset-title");

    let existingNames = Object.values(existing).map(x => x.innerText);



    if(existingNames.includes(presetName)){

        if (confirm("Preset Name exists - overwrite it?")){

            return true;
            
        } else {

            return false;
            
        }

    } else {
    
        return true;

    }

    
    

}
   
function checkScriptName(){

    // which preset div is selected?

    scriptName = document.querySelectorAll("[data-selectedForm]")[0].getElementsByTagName("input")[0].value.trim();
    scriptDescription = document.querySelectorAll("[data-selectedForm]")[0].getElementsByTagName("input")[1].value.trim();
    scriptCommands = document.querySelectorAll("[data-selectedForm]")[0].getElementsByTagName("textarea")[0].value.trim();

    if (scriptName === '' || scriptDescription=== '' || scriptCommands===''){
        showAlert("All 3 fields must be completed.");
        return false;
    }

    scriptFileName = scriptName.toLowerCase().replace(/\ /g, "_") + ".json";

    let existing = document.getElementsByClassName("preset-list-item"); // data-preset-menu

    let existingNames = Object.values(existing).map(x => x.dataset.presetMenu);



    if(existingNames.includes(scriptFileName)){

        if (confirm("Script Name exists - overwrite it?")){

            
            return true;
 
            
        } else {

            return false;
            
        }

    } else {
    
        return true;

    }

    
    
    

}
    
    
