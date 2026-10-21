/* =========================================================
   SmartCampus - Global Theme Controller
   Dark / Light Mode
   ========================================================= */

(function () {
    "use strict";

    const STORAGE_KEY = "smartcampus-theme";


    /* =====================================================
       GET SAVED THEME
       ===================================================== */

    function getSavedTheme() {

        const savedTheme =
            localStorage.getItem(STORAGE_KEY);

        if (
            savedTheme === "dark" ||
            savedTheme === "light"
        ) {
            return savedTheme;
        }

        return "light";
    }


    /* =====================================================
       APPLY THEME
       ===================================================== */

    function applyTheme(theme) {

        const isDark =
            theme === "dark";

        /* HTML theme attribute */
        document.documentElement.setAttribute(
            "data-theme",
            isDark ? "dark" : "light"
        );

        /* Body class */
        document.body.classList.toggle(
            "sc-dark-mode",
            isDark
        );

        /* Save preference */
        localStorage.setItem(
            STORAGE_KEY,
            isDark ? "dark" : "light"
        );

        updateThemeButton();
    }


    /* =====================================================
       UPDATE BUTTON
       ===================================================== */

    function updateThemeButton() {

        const button =
            document.getElementById(
                "scThemeToggle"
            );

        if (!button) {
            return;
        }

        const isDark =
            document.body.classList.contains(
                "sc-dark-mode"
            );


        if (isDark) {

            button.innerHTML =
                '<i class="bi bi-sun-fill"></i>';

            button.setAttribute(
                "title",
                "Switch to Light Mode"
            );

            button.setAttribute(
                "aria-label",
                "Switch to Light Mode"
            );

        } else {

            button.innerHTML =
                '<i class="bi bi-moon-stars-fill"></i>';

            button.setAttribute(
                "title",
                "Switch to Dark Mode"
            );

            button.setAttribute(
                "aria-label",
                "Switch to Dark Mode"
            );
        }
    }


    /* =====================================================
       CREATE THEME BUTTON
       ===================================================== */

    function createThemeButton() {

        /* Don't create twice */
        if (
            document.getElementById(
                "scThemeToggle"
            )
        ) {
            return;
        }


        const button =
            document.createElement("button");


        button.type = "button";

        button.id =
            "scThemeToggle";

        button.className =
            "sc-theme-toggle";


        button.setAttribute(
            "aria-label",
            "Switch to Dark Mode"
        );

        button.setAttribute(
            "title",
            "Switch to Dark Mode"
        );


        /* =================================================
           BUTTON CLICK
           ================================================= */

        button.addEventListener(
            "click",
            function () {

                const currentTheme =
                    document.body.classList.contains(
                        "sc-dark-mode"
                    )
                        ? "dark"
                        : "light";


                const newTheme =
                    currentTheme === "dark"
                        ? "light"
                        : "dark";


                applyTheme(newTheme);
            }
        );


        /* =================================================
           FIND NAVBAR
           ================================================= */

        const navbarActions =
            document.querySelector(
                ".navbar .d-flex.align-items-center"
            );


        if (navbarActions) {

            navbarActions.insertBefore(
                button,
                navbarActions.firstChild
            );

            return;
        }


        /* SmartCampus custom navbar */

        const smartCampusNavbar =
            document.querySelector(
                ".sms-navbar .d-flex.align-items-center"
            );


        if (smartCampusNavbar) {

            smartCampusNavbar.insertBefore(
                button,
                smartCampusNavbar.firstChild
            );

            return;
        }


        /* Generic navbar */

        const genericNavbar =
            document.querySelector(
                "nav .d-flex"
            );


        if (genericNavbar) {

            genericNavbar.insertBefore(
                button,
                genericNavbar.firstChild
            );

            return;
        }


        /* =================================================
           FALLBACK
           ================================================= */

        button.classList.add(
            "sc-theme-toggle-floating"
        );

        document.body.appendChild(
            button
        );
    }


    /* =====================================================
       INITIALIZE
       ===================================================== */

    function initializeTheme() {

        const savedTheme =
            getSavedTheme();


        /* Apply saved theme */
        applyTheme(
            savedTheme
        );


        /* Create button */
        createThemeButton();


        /* Update icon */
        updateThemeButton();
    }


    /* =====================================================
       START AFTER PAGE LOAD
       ===================================================== */

    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initializeTheme
        );

    } else {

        initializeTheme();
    }

})();
