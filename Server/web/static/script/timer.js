const Timer = {
    activeNavMenuCls: 'link-secondary',

    // Highlight the currently active nav menu item
    setNavMenu: () => {
        "use strict";
        let path = window.location.pathname;

        document.querySelectorAll('[href="' + path + '"]').forEach(el => { 
            el.classList.add(Timer.activeNavMenuCls); 
        });
    },
}

Timer.setNavMenu();