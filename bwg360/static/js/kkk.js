/**
 * Created by ism on 17-6-17.
 */

function setCookie(name,value,days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}
function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}
function eraseCookie(name) {
    document.cookie = name+'=; Max-Age=-99999999;';
}
$(document).ready(function () {
    // setInterval(function(){
    //     if(!document.getElementById('ZkShUOPClorWRTsaOPQDAfd8')){
    //       document.getElementById('ADAKZGYiRpNHfMQ').style.display='block';
    //     }
    //  }, 5000)
    setTimeout(function(){
        var options = {
            swfContainerId: '',
            swfPath: '',
            userDefinedFonts: [],
            excludeUserAgent: true,
            excludeLanguage: true,
            excludeColorDepth: true,
            excludeScreenResolution: false,
            excludeAvailableScreenResolution: false,
            excludeTimezoneOffset: true,
            excludeSessionStorage: true,
            excludeIndexedDB: true,
            excludeAddBehavior: true,
            excludeOpenDatabase: true,
            excludeCpuClass: false,
            excludePlatform: false,
            excludeDoNotTrack: true,
            excludeCanvas: false,
            excludeWebGL: true,
            excludeAdBlock: true,
            excludeHasLiedLanguages: true,
            excludeHasLiedResolution: true,
            excludeHasLiedOs: true,
            excludeHasLiedBrowser: true,
            excludeJsFonts: true,
            excludeFlashFonts: true,
            excludePlugins: true,
            excludeIEPlugins: true,
            excludeTouchSupport: true,
            excludePixelRatio: false,
            excludeHardwareConcurrency: false,
            excludeWebGLVendorAndRenderer: false,
            excludeDeviceMemory: false,
        }
        new Fingerprint2(options).get(function(result, components) {
            setCookie('fppkcookie', result, 7);
        });
    }, 500)
})