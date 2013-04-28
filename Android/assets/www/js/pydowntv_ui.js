
/*  Pull Updates */
var UpdateHistory = new Lungo.Element.Pull('#History', {
    onPull: "Desliza para actulizar",
    onRelease: "Suelta ;)",
    onRefresh: "Actualizando",
    callback: function() {
        UpdateHistory.hide();
    }
});