// https://github.com/botui/botui
// start rasa with the following cmd: rasa run --enable-api --auth-token pass --cors "*"

function generateId(length) {
  var result = "";
  var characters =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  var charactersLength = characters.length;
  for (var i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
  }
  console.log("ID: " + result)
  return result;
}

const rasaServer = "http://localhost:5005/webhooks/rest/webhook?token=pass";
const id = generateId(8);

function init() {
  var botui = new BotUI("app"); // id of container
  botui.message
    .bot({
      delay: 200,
      content: "Hallo, ich bin ein Bot!",
    })
    .then(function () {
      botui.message.bot({
        delay: 1000, // wait 1 sec.
        loading: true,
        content:
          "Ich kann dir bei verschiedensten Angelegenheiten rund ums Bürgeramt helfen. Frag mich einfach etwas.",
      });
    })
    .then(function () {
      let prom = new Promise((res, rej) => {
        res(showTextField(botui));
      });
      return prom;
    });
}

function showTextField(botui) {
  botui.action
    .text({
      delay: 1000,
      cssClass: "custom-class",
      autoHide: true,
      action: {
        placeholder: "Hier Text eingeben...",
      },
    })
    .then(function (txt) {
      let prom = new Promise((res, rej) => {
        response = getResponse(txt.value);
        res(response);
      });
      return prom;
    })
    .then(function (res) {
      botui.message.bot({
        delay: 1000,
        loading: true,
        content: res,
      });
    })
    .then(function () {
      let prom = new Promise((res, rej) => {
        res(showTextField(botui));
      });
      return prom;
    });
}

async function getResponse(msg) {
  var msg = {
    sender: id,
    message: msg,
  };
  const response = await fetch(rasaServer, {
    method: "POST",
    body: JSON.stringify(msg),
    headers: {
      "Content-Type": "application/json",
    },
  });
  const data = await response.json();
  try {
    return data[0]["text"];
  } catch {
    return "Tut mir leid, da habe ich etwas nicht verstanden. Könntest du es umformulieren?";
  }
}

init();
