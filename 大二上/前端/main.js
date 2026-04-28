// 这是一个JS注释：这段代码会在浏览器的控制台打印一条消息
console.log("你好，我的智能家居系统已经启动！");

// 让我们来增加一点交互
// 当用户点击 h1 标题时，弹出一个警告框
const heading = document.querySelector('h1'); // 找到 h1 标题元素
heading.addEventListener('click', () => {
  alert('别点我，我怕疼！');
});