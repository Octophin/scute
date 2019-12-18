/////////////////////////////
// future SCUTE development 
// will re-work these functions.
/////////////////////////////


// Replace with general form and data attribute system. This is huge and unnecessarily so

let triggerAction = function (e) {

    if (!getSelectedDevices().length) {

        return false;

    }

    let element = e.currentTarget;

    if (element.hasAttribute("disabled")) {

        return false;

    }

    let value;

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


// Replace with new showConfirm

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


// called from above... refactor...

let okClickProcess = function (targetURL){

    // close the poptp this came from and redirect the page
    document.getElementById('popup').outerHTML = '';
    document.location.href = targetURL;

};


// Make new popup code for alerts and confirms

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

// Again maybe move to CSS. Or have a general toggle system that works for everything with data attributes

let uploadPreset = function () {

    document.querySelectorAll("[data-preset]").forEach(function (element) {

        element.style.display = "none";

    });

    document.querySelector("[data-preset='upload']").style.display = "block";

};

// Same as comment on load scripts. replace with CSS.

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


// As with other bits this confirm should be in the HTML attributes (also allows translation and such in the future)
// System wide there should never be any text directly in the JavaScript

let deletePreset = function () {

    let preset = document.querySelector("[data-preset-menu][data-selected]").getAttribute("data-preset-menu");

    if (preset) {

        showConfirm("Are you sure you want to delete " + preset + " ?", "/presets?delete=" + preset);

    }

};


// This should be done via CSS! Ask Remi!

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



// Should all showConfirm buttons actually just be a series of data attributes in HTML saying the confirm message?
// We shouldn't have lots of these.

// For preloaded scripts we simply shouldn't show the delete button. This can be done in Jinja. With title text on the button.

// Use script types or categories for this.

// Therefore this function should go!

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


// This (like script name checking should happen on the server side only)
    
function checkPresetName(){

    // which preset div is selected?

    let presetName = document.querySelectorAll("[data-selectedForm]")[0].getElementsByTagName("input")[0].value.trim();

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

// This should be an error return from the form which asks whether you should overwrite existing.
// "Filename already exists - do you wish to overwrite?"
   
function checkScriptName(){

    // which preset div is selected?

    let scriptName = document.querySelectorAll("[data-selectedForm]")[0].getElementsByTagName("input")[0].value.trim();
    let scriptDescription = document.querySelectorAll("[data-selectedForm]")[0].getElementsByTagName("input")[1].value.trim();
    let scriptCommands = document.querySelectorAll("[data-selectedForm]")[0].getElementsByTagName("textarea")[0].value.trim();

    if (scriptName === '' || scriptDescription=== '' || scriptCommands===''){
        showAlert("All 3 fields must be completed.");
        return false;
    }

    let scriptFileName = scriptName.toLowerCase().replace(/\ /g, "_") + ".json";

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


// Burger Menu
// Make this CSS only!

function toggleBurger() {
    document.body.toggleAttribute("data-open");
}
toggleBurger();




