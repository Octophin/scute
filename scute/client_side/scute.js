document.querySelectorAll(".deviceHeader").forEach(function (element) {

    element.addEventListener("click", function (e) {

        let element = e.currentTarget;

        if (element.getAttribute("data-active")) {

            element.removeAttribute("data-active");

        } else {

            element.setAttribute("data-active", "true");

        }

        let selected = document.querySelectorAll(".deviceHeader[data-active]");

        if (selected.length) {

            document.querySelector(".actions").style.visibility = "visible";
            document.querySelector(".selected-devices .count").innerHTML = selected.length;

        } else {

            document.querySelector(".actions").style.visibility = "hidden";

        }

    });

});

let clearDevices = function () {

    document.querySelector(".actions").style.visibility = "hidden";

    document.querySelectorAll(".deviceHeader[data-active]").forEach(function (element) {

        element.removeAttribute("data-active");

    });

};

document.querySelectorAll("input, select").forEach(function (element) {

    element.addEventListener("change", function (e) {

        if (e.target.value) {

            e.target.setAttribute("data-changed", "true");

        } else {

            e.target.removeAttribute("data-changed");

        }


    });

});

let triggerAction = function(action){
    
    console.log(action);    

};
