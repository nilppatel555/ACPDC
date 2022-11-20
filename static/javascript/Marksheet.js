const imgBox = document.querySelector(".js");

var uploaded_img = "";


imgBox.addEventListener("change",function(){
    const reader = new FileReader();
    reader.addEventListener("load",()=> {
        uploaded_img = reader.result;
        document.querySelector("#display_img").style.backgroundImage = `url(${uploaded_img})`;
    });
    reader.readAsDataURL(this.files[0]);
})


