let getSelectedDevices = function () {

    let selected = Array.from(document.querySelectorAll(".deviceHeader[data-active]"));

    return selected.map(function (element) {

        return element.getAttribute("data-device");

    });

};


document.querySelectorAll(".deviceHeader").forEach(function (element) {

    element.addEventListener("click", function (e) {

        let element = e.currentTarget;

        if (element.getAttribute("data-active")) {

            element.removeAttribute("data-active");

        } else {

            element.setAttribute("data-active", "true");

        }

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

                    element.setAttribute("disabled", true);

                });

            }

        } else {

            Array.from(document.querySelectorAll(".buttons-wrapper select, .buttons-wrapper button")).forEach(function (element) {

                element.setAttribute("disabled", true);

            });


        }

    });

});

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

    if (element.tagName.toLowerCase() === "select") {

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

    if (element.hasAttribute("data-warn")) {

        let warning = "Apply " + element.innerHTML + " to " + selectedDevices.toString() + "?";

        showConfirm(warning, targetURL);

        return false;

    } else {

        document.location.href = targetURL;

    }

};

let showConfirm = function (warning, targetURL) {

    // Remove existing popup

    if (document.getElementById("popup")) {

        document.getElementById("popup").outerHTML = "";

    }

    let popup = `<section id="popup" class="are-you-sure">
                    <div class="pop-up navy">
                        <p>${warning}</p>
                        <div class="pop-up-buttons">
                            <button onclick="document.location.href='${targetURL}'">Yes</button>
                            <button onclick="document.getElementById('popup').outerHTML = ''">No</button>
                        </div>
                    </div>
                </section>`;

    document.querySelector("main").insertAdjacentHTML("afterbegin", popup);

};


let savePreset = function () {

    let values = {};

    document.querySelectorAll("input, select").forEach(function (element) {

        // Ignore if exclude from preset

        if (element.parentElement.getAttribute("data-exlude-from-preset")) {

            return false;

        }

        let name = element.getAttribute("name");
        let value;

        if (element.tagName === "SELECT") {

            value = element.options[element.selectedIndex].value;

        } else {

            value = element.value;

        }

        values[name] = value;

    });

    alert("Not yet implemented but data will be " + JSON.stringify(values));

};

let loadPreset = function (presetID) {

    document.querySelectorAll("[data-preset]").forEach(function (element) {

        if (element.getAttribute("data-preset") === presetID) {

            element.style.display = "revert";

        } else {

            element.style.display = "none";

        }

    });

};

