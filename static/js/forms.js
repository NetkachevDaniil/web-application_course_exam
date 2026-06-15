function initEasyMDE(elementId, minHeight) {
    const element = document.getElementById(elementId);
    if (!element) {
        return null;
    }

    const editor = new EasyMDE({
        element: element,
        spellChecker: false,
        status: false,
        forceSync: true,
        minHeight: minHeight || "150px",
    });

    const form = element.closest("form");
    if (form) {
        form.addEventListener("submit", function () {
            editor.codemirror.save();
        });
    }

    return editor;
}
