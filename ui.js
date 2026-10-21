/* SmartCampus UI enhancer: adds icons to page titles and buttons, no content removed */
(function () {
  "use strict";
  var TITLE_ICONS = [
    [/dashboard|welcome|overview/i, "bi-speedometer2"], [/attendance/i, "bi-calendar-check-fill"],
    [/assignment/i, "bi-journal-text"], [/announcement/i, "bi-megaphone-fill"], [/timetable|schedule/i, "bi-clock-history"],
    [/profile/i, "bi-person-badge-fill"], [/student/i, "bi-people-fill"], [/faculty/i, "bi-person-workspace"],
    [/exam/i, "bi-pencil-square"], [/register|sign up/i, "bi-person-plus-fill"], [/login/i, "bi-box-arrow-in-right"]
  ];
  var FIELD_ICONS = [
    [/name|student name|faculty name/i, "bi-person-fill"],
    [/email|e-mail/i, "bi-envelope-fill"],
    [/password/i, "bi-lock-fill"],
    [/phone|mobile|contact/i, "bi-telephone-fill"],
    [/course|subject/i, "bi-book-fill"],
    [/semester|term/i, "bi-layers-fill"],
    [/batch/i, "bi-collection-fill"],
    [/division|section/i, "bi-diagram-3-fill"],
    [/roll|register|student id|campus id/i, "bi-person-vcard-fill"],
    [/date of birth|dob|date/i, "bi-calendar-event-fill"],
    [/gender/i, "bi-gender-ambiguous"],
    [/address|location/i, "bi-geo-alt-fill"],
    [/title|heading/i, "bi-type-bold"],
    [/message|description|details/i, "bi-chat-left-text-fill"],
    [/attendance/i, "bi-calendar-check-fill"],
    [/status/i, "bi-check2-square"],
    [/file|document|attachment/i, "bi-paperclip"],
    [/search/i, "bi-search"],
    [/announcement/i, "bi-megaphone-fill"],
    [/assignment/i, "bi-journal-text"],
    [/timetable|schedule/i, "bi-clock-fill"]
  ];
  var BTN_ICONS = [
    [/^\s*(logout|log out)/i, "bi-box-arrow-right"], [/^\s*(save|update)/i, "bi-check2-circle"],
    [/^\s*(add|create|post|publish)/i, "bi-plus-circle-fill"], [/^\s*delete|remove/i, "bi-trash3-fill"],
    [/^\s*edit/i, "bi-pencil-fill"], [/^\s*(view|open)/i, "bi-eye-fill"], [/^\s*(search|filter)/i, "bi-search"],
    [/^\s*(submit|register)/i, "bi-send-fill"], [/^\s*(cancel|back)/i, "bi-arrow-left-circle"],
    [/^\s*(download|export)/i, "bi-download"], [/^\s*(change password|password)/i, "bi-key-fill"]
  ];
  function pick(list, text) {
    for (var i = 0; i < list.length; i++) if (list[i][0].test(text)) return list[i][1];
    return null;
  }
  function init() {
    document.querySelectorAll("main h2, .container h2, .container-fluid h2, .page-header h1, .page-header h2").forEach(function (h) {
      if (h.querySelector("i.bi") || h.closest(".card") || h.querySelector(".page-icon")) return;
      var ic = pick(TITLE_ICONS, h.textContent);
      if (!ic) return;
      var s = document.createElement("span");
      s.className = "page-icon"; s.innerHTML = '<i class="bi ' + ic + '"></i>';
      h.insertBefore(s, h.firstChild);
    });
    document.querySelectorAll("button.btn, a.btn, input[type=submit].btn").forEach(function (b) {
      if (b.querySelector("i.bi") || b.tagName === "INPUT" || b.classList.contains("btn-close")) return;
      var ic = pick(BTN_ICONS, b.textContent);
      if (!ic) return;
      var i = document.createElement("i");
      i.className = "bi " + ic + " me-2"; b.insertBefore(i, b.firstChild);
    });
    document.querySelectorAll("aside .nav-link, .student-sidebar a").forEach(function (a) {
      if (a.querySelector("i.bi")) return;
      var ic = pick(TITLE_ICONS, a.textContent) || "bi-circle";
      var i = document.createElement("i"); i.className = "bi " + ic; a.insertBefore(i, a.firstChild);
    });
    document.querySelectorAll("label.form-label, .form-label").forEach(function (label) {
      if (label.querySelector("i.bi")) return;
      var ic = pick(FIELD_ICONS, label.textContent);
      if (!ic) return;
      var i = document.createElement("i");
      i.className = "bi " + ic + " me-1";
      label.insertBefore(i, label.firstChild);
    });

    document.querySelectorAll("input.form-control, textarea.form-control, select.form-select").forEach(function (field) {
      if (field.getAttribute("aria-label") || field.placeholder) return;
      var label = field.id ? document.querySelector('label[for="' + CSS.escape(field.id) + '"]') : null;
      if (label && label.textContent) {
        var ic = pick(FIELD_ICONS, label.textContent);
        if (ic) field.setAttribute("data-field-icon", ic);
      }
    });

    document.querySelectorAll(".alert").forEach(function (a) {
      if (a.querySelector("i.bi")) return;
      var map = { success: "bi-check-circle-fill", danger: "bi-exclamation-octagon-fill", warning: "bi-exclamation-triangle-fill", info: "bi-info-circle-fill" };
      for (var k in map) if (a.classList.contains("alert-" + k)) {
        var i = document.createElement("i"); i.className = "bi " + map[k] + " me-2"; a.insertBefore(i, a.firstChild); break;
      }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
