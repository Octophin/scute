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

function displayLoadingPopup() {
    document.getElementById("loadingPopup").style.display = "block";
    lockScreenOverlay();
}

function lockScreenOverlay() {

    document.getElementById("clickOverlay").style.display = "block";
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

        return confirm(message);
        
        //showConfirm(message, '', false, ["Save To Preset","Cancel"], theForm.id );

 
        }

}


// This is a variant of jQuery show / hide. But maybe we should have a toggle / switch css variant
// Fine to leave

function showHideDiv(targetID) {

    let x = document.getElementById(targetID);
    if (x.style.display === "none" || x.style.display === "") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }

}

// This is fine, could maybe improve to check if the previous change is different
// I have done this before by adding a data-attribute for the original value in the template (Jinja)

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
