import cityData from "./id_city.json" assert { type: "json" };
import secrets from "./secrets.json" assert { type: "json" };

window.onload = function () {
  let modal = document.getElementById("nerdmodal");
  let alertmodal = document.getElementById("alertmodal");
  let startDate = document.getElementById("start");
  let endDate = document.getElementById("end");
  let submitbutton = document.getElementById("submitbutton");
  let metryKey = secrets.secrets.metry_key;

  document.getElementById("ddlCity").onchange = function () {
    while (document.getElementById("meters").lastElementChild) {
      document
        .getElementById("meters")
        .removeChild(document.getElementById("meters").lastElementChild);
    }

    document.getElementById("meters").style.display = "inline-block";
    document.getElementById("meter_label").style.display = "inline-block";
    let defaultOption = document.createElement("option");
    defaultOption.value = "none";
    defaultOption.text = "Alla anläggningar";
    document.getElementById("meters").appendChild(defaultOption);
    let selectedCity = document.getElementById("ddlCity").value;
    Object.keys(cityData).forEach((obj) => {
      console.log(cityData[obj]);
      if (cityData[obj]["city"] == selectedCity) {
        fetch(
          `https://app.metry.io/api/2.0/meters/${obj}?access_token=${metryKey}`
        )
          .then((response) => response.json())
          .then((data) => {
            let option = document.createElement("option");
            option.value = obj;
            option.text = data["data"].name;
            document.getElementById("meters").appendChild(option);
          });
      }
    });
  };
  document.getElementById("ddlCityAlert").onchange = function () {
    while (document.getElementById("meters_alert").lastElementChild) {
      document
        .getElementById("meters_alert")
        .removeChild(document.getElementById("meters_alert").lastElementChild);
    }

    document.getElementById("meters_alert").style.display = "inline-block";
    document.getElementById("meter_label_alert").style.display = "inline-block";
    let defaultOption = document.createElement("option");
    defaultOption.value = "none";
    defaultOption.text = "Alla anläggningar";
    document.getElementById("meters").appendChild(defaultOption);
    let selectedCity = document.getElementById("ddlCityAlert").value;
    Object.keys(cityData).forEach((obj) => {
      console.log(cityData[obj]);
      if (cityData[obj]["city"] == selectedCity) {
        fetch(
          `https://app.metry.io/api/2.0/meters/${obj}?access_token=${metryKey}`
        )
          .then((response) => response.json())
          .then((data) => {
            let option = document.createElement("option");
            option.value = obj;
            option.text = data["data"].name;
            document.getElementById("meters_alert").appendChild(option);
          });
      }
    });
  };
  document.getElementById("nerdbutton").onclick = function () {
    modal.style.display = "flex";
    wrapper.style.overflowY = "none";
  };
  // When the user clicks on <span> (x), close the modal
  document.getElementById("nerdmodalclose").onclick = function () {
    modal.style.display = "none";
  };

  // When the user clicks anywhere outside of the modal, close it
  window.onclick = function (event) {
    if (event.target == modal || event.target == alertmodal) {
      alertmodal.style.display = "none";
      modal.style.display = "none";
    }
  };

  document.getElementById("alertbutton").onclick = function () {
    alertmodal.style.display = "flex";
    wrapper.style.overflowY = "none";
  };
  // When the user clicks on <span> (x), close the modal
  document.getElementById("alertmodalclose").onclick = function () {
    alertmodal.style.display = "none";
  };

  startDate.onchange = function () {
    submitbutton.disabled = false;
  };
  endDate.onchange = function () {
    submitbutton.disabled = false;
  };

  submitbutton.onclick = function () {
    if (endDate.value < startDate.value) {
      console.log("hej");
      submitbutton.disabled = true;
      submitbutton.classList.add("apply-shake");
    }
  };
};
