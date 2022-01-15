// https://github.com/botui/botui
// start rasa with the following cmd: rasa run --enable-api --auth-token pass --cors "*"

var botui = new BotUI("app"); // id of container
const socket = io("http://localhost:5005");

function init() {
  receiveMsg();
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
        res(showTextField());
      });
      return prom;
    });
}

function showTextField() {
  botui.action
    .text({
      delay: 1000,
      autoHide: false,
      action: {
        placeholder: "Hier Text eingeben...",
      },
    })
    .then(function (txt) {
      sendMsg(txt.value);
    });
}

async function sendMsg(msg) {
  socket.emit("user_uttered", {
    message: msg,
  });
}

function receiveMsg() {
  socket.on("bot_uttered", function (response) {
    console.log(response);
    if (response.text) {
      botui.message.bot({
        delay: 1000,
        loading: true,
        content: response.text,
      });
    }
    handleButtons();
  });
}

function handleButtons() {
  botui.action
    .button({
      action: [
        {
          text: "Wohnung anmelden",
          value: "button",
        },
        {
          text: "Etwas anderes",
          value: "text",
        },
      ],
    })
    .then(function (res) {
      // will be called when a button is clicked.
      if (res.value === "button") {
        sendMsg(res.text);
      }
    })
    .then(function (res) {
      let prom = new Promise((res, rej) => {
        res(showTextField());
      });
      return prom;
    });
}

init();
