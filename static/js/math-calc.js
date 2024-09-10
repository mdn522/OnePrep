// Draggable Window Script
let mg_starting_z_index = 200;
let windowWidth = window.innerWidth;
let windowHeight = window.innerHeight;
window.addEventListener('load', function () {
    initDragElement();
    initResizeElement();
});

function initDragElement() {
    let pos1 = 0,
        pos2 = 0,
        pos3 = 0,
        pos4 = 0;
    let popups = document.getElementsByClassName("mg-popup");
    let element = null;
    let currentZIndex = mg_starting_z_index; // TODO reset z index when a threshold is passed

    for (var i = 0; i < popups.length; i++) {
        var popup = popups[i];
        var header = getHeader(popup);

        popup.onmousedown = function () {
            this.style.zIndex = "" + ++currentZIndex;
        };

        if (header) {
            header.parentPopup = popup;
            header.onmousedown = dragMouseDown;
        }
    }

    function dragMouseDown(e) {
        element = this.parentPopup;
        element.style.zIndex = "" + ++currentZIndex;

        e = e || window.event;
        // get the mouse cursor position at startup:
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        // call a function whenever the cursor moves:
        document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
        if (!element) {
            return;
        }

        e = e || window.event;
        // calculate the new cursor position:
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        // set the element's new position:
        // elmnt.style.top = elmnt.offsetTop - pos2 + "px";
        // elmnt.style.left = elmnt.offsetLeft - pos1 + "px";
        // modify to prevent out of bound x and y using window width and height
        element.style.top = Math.min(windowHeight - 50, Math.max(5, element.offsetTop - pos2)) + "px";
        element.style.left = Math.min(windowWidth - 50, Math.max(5, element.offsetLeft - pos1)) + "px";
        // element.style.top = Math.max(5, element.offsetTop - pos2) + "px";
        // element.style.left = Math.max(5, element.offsetLeft - pos1) + "px";
    }

    function closeDragElement() {
        /* stop moving when mouse button is released:*/
        document.onmouseup = null;
        document.onmousemove = null;
        let calc = Alpine.store('calculator');
        calc.x = parseInt(element.style.left, 10);
        calc.y = parseInt(element.style.top, 10);
        // calc.x = Math.max(5, element.offsetLeft - pos1);
        // calc.y = Math.max(5, element.offsetTop - pos2);
    }

    function getHeader(element) {
        var headerItems = element.getElementsByClassName("mg-popup-top");

        if (headerItems.length === 1) {
            return headerItems[0];
        }

        return null;
    }
}

function initResizeElement() {
    let popups = document.getElementsByClassName("mg-popup");

    let element = null;
    let startX, startY, startWidth, startHeight;

    for (let i = 0; i < popups.length; i++) {
        let p = popups[i];
        if (p.classList.contains('mg-no-resizer')) {
            continue;
        }

        let right = document.createElement("div");
        right.className = "resizer-right";
        p.appendChild(right);
        right.addEventListener("mousedown", initDrag, false);
        right.parentPopup = p;

        let bottom = document.createElement("div");
        bottom.className = "resizer-bottom";
        p.appendChild(bottom);
        bottom.addEventListener("mousedown", initDrag, false);
        bottom.parentPopup = p;

        let both = document.createElement("div");
        both.className = "resizer-both";
        p.appendChild(both);
        both.addEventListener("mousedown", initDrag, false);
        both.parentPopup = p;
    }

    function initDrag(e) {
        element = this.parentPopup;

        startX = e.clientX;
        startY = e.clientY;
        startWidth = parseInt(
            document.defaultView.getComputedStyle(element).width,
            10
        );
        startHeight = parseInt(
            document.defaultView.getComputedStyle(element).height,
            10
        );
        document.documentElement.addEventListener("mousemove", doDrag, false);
        document.documentElement.addEventListener("mouseup", stopDrag, false);
    }

    function doDrag(e) {
        element.style.width = startWidth + e.clientX - startX + "px";
        element.style.height = startHeight + e.clientY - startY + "px";
        // console.log('do drag', element.style.width, element.style.height);
    }

    function stopDrag(e) {
        let calc = Alpine.store('calculator');
        // console.log('stop drag', element.style.width, element.style.height);
        calc.width = parseInt(element.style.width, 10);
        calc.height = parseInt(element.style.height, 10);
        document.documentElement.removeEventListener(
            "mousemove",
            doDrag,
            false
        );
        document.documentElement.removeEventListener(
            "mouseup",
            stopDrag,
            false
        );
    }
}

// Popup
document.addEventListener("click", (e) => {
    // Close
    if (e.target.closest(".mg-popup-close")) {
        // e.target.closest(".mg-popup").style.visibility = "hidden";
        Alpine.store('calculator').show = false;
        // let key = e.target.closest(".mg-popup").getAttribute('data-key');
        // if (key) {
        //     Alpine.store('windows')['show_' + key] = false;
        // }
    }

    // Minimize
    if (e.target.closest(".mg-popup-minimize")) {
        Alpine.store('calculator').minimized = !Alpine.store('calculator').minimized;
        // e.target.closest(".mg-popup").classList.toggle("mg-popup-minimized");
    }
});

document.addEventListener("mousedown", (e) => {
    if (e.target.closest(".mg-popup")) {
        // mg_starting_z_index += 1;
        e.target.closest(".mg-popup").style.zIndex = mg_starting_z_index;
    }
});

document.addEventListener("dblclick", (e) => {
    if (e.target.closest(".mg-popup-top")) {
        // e.target.closest(".mg-popup").classList.toggle("mg-popup-minimized");
        Alpine.store('calculator').minimized = !Alpine.store('calculator').minimized;

    }
});

function calc_resize() {
      // resize calculator. fix out of bounds x,y and width height
    let calc = Alpine.store('calculator');
    let calcEl = document.getElementById('calculator-window');
    let calcWidth = calcEl.offsetWidth;
    let calcHeight = calcEl.offsetHeight;
    let calcX = calc.x;
    let calcY = calc.y;
    windowWidth = window.innerWidth;
    windowHeight = window.innerHeight;

    if (calcX + calcWidth > windowWidth) {
        calc.x = Math.max(windowWidth - calcWidth, 5);
    }
    if (calcY + calcHeight > windowHeight) {
        calc.y = Math.max(windowHeight - calcHeight, 5);
    }
    // if x and y reaches min then resize the window width and height till min width and height reached
    if (calc.x <= 5 && (calcWidth + calc.x) > windowWidth) {
        calc.width = windowWidth - calc.x - 25;
    }
    if (calc.y <= 5 && (calcHeight + calc.y) > windowHeight) {
        calc.height = windowHeight - calc.y - 25;
    }

    // console.log('resize', calc.x, calc.y, calcWidth, calcHeight, windowWidth, windowHeight);

}

// document on resize
window.addEventListener('resize', (e) => {
    calc_resize();
})

// End Draggable
