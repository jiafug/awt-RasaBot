// https://github.com/botui/botui

var botui = new BotUI("app"); // id of container
const socket = io("http://localhost:5005");

/**
 * Called upon loading the webpage and greets the user.
 */
function init() {
  // websocket init to receive messages
  receiveMsg();
  // show greeting messages to user
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
    });
}

/**
 * Sends a message to the rasa server through a websocket channel.
 * @param {*} msg
 */
async function sendMsg(msg) {
  console.log("msg sent: " + msg);
  socket.emit("user_uttered", {
    message: msg,
  });
}

/**
 * The functions registers the receive channel of the websocket connection
 * to the rasa server backend.
 */
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
    if (response.quick_replies) {
      handleButtons(response);
    }
  });
}

/**
 * This function handles button responses by the rasa server.
 * @param {*} response
 */
function handleButtons(response) {
  buttons = [];
  for (let i = 0; i < response.quick_replies.length; i++) {
    title = response.quick_replies[i]["title"];
    payload = response.quick_replies[i]["title"];
    msg = {
      text: title,
      value: payload,
    };
    buttons.push(msg);
  }
  botui.action
    .button({
      action: buttons,
    })
    .then(function (res) {
      sendMsg(res.value);
    });
}

function showTextInput() {
  const div = document.createElement("div");

  div.className = "text-outer-wrapper";

  div.innerHTML = `
    <div class="text-input-container">
      <div class="text-input-inner">
        <form onsubmit="sendUserText();return false" class="">
          <input placeholder="Hier Text eingeben..." required="required" class="text-input-inner-field" id="user"> 
          <button type="button" class="text-input-inner-submit" onclick="sendUserText()">
            <img src="./senden.png" width="14" height="14">
          </button>
        </form>
      </div>
    </div>
  `;

  document.getElementById("main-container").appendChild(div);
}

function sendUserText() {
  text = document.getElementById("user").value;
  botui.message.add({
    human: true,
    content: text,
  });
  sendMsg(text);
  document.getElementById("user").value = "";
}

document.addEventListener("DOMContentLoaded", function (event) {
  // bot init
  init();
  showTextInput();
});
