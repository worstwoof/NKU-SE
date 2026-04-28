// === 获取所有需要操作的 DOM 元素 ===
const displayElement = document.getElementById('display');
const subDisplayElement = document.getElementById('sub-display');
const buttonsContainer = document.getElementById('buttons-container');
const historyList = document.getElementById('history-list');
const clearHistoryButton = document.getElementById('clear-history');
const themeToggle = document.getElementById('theme-toggle');
const modeToggle = document.getElementById('mode-toggle');
const calculatorElement = document.getElementById('calculator');

// === 状态变量 ===
let currentInput = '0';       
let currentExpression = '';   
let justCalculated = false; // 标记是否刚按下了 "="
let history = []; // 内存中的历史记录数组

// === 用于区分输入的特殊类型 ===
// 用于区分 sin( 这类需要加括号的输入
const prefixFunctions = ['sin', 'cos', 'tan', 'log', 'ln', '√'];
// 用于处理 π 这类常量
const constants = ['π'];

// === 初始化 ===
// 页面加载时，恢复用户上次的设置
loadTheme();
loadMode();
loadHistory();
updateDisplay();

// === 事件监听器 ===

// 事件委托：只在父元素上监听一次点击，提高性能
buttonsContainer.addEventListener('click', (event) => {
    // 确保点击的是按钮
    if (!event.target.matches('.btn')) return;
    const value = event.target.dataset.value;
    handleInput(value); // 转交给核心处理器
});

// 监听整个文档的键盘事件
document.addEventListener('keydown', (event) => {
    const key = event.key;
    let value = null;

    // 映射键盘按键到 data-value
    if (/\d/.test(key)) value = key;
    else if (key === '.') value = '.';
    else if (key === '+') value = '+';
    else if (key === '-') value = '-';
    else if (key === '*') value = 'x';
    else if (key === '/') { event.preventDefault(); value = '/'; } // 阻止浏览器默认行为
    else if (key === '%') value = '%';
    else if (key === '(') value = '(';
    else if (key === ')') value = ')';
    else if (key === '^') value = '^';
    else if (key === 'Enter' || key === '=') { event.preventDefault(); value = '='; }
    else if (key === 'Backspace') value = 'DEL';
    else if (key === 'Escape') value = 'AC';
    
    if (value) handleInput(value);
});

// 清除历史记录按钮
clearHistoryButton.addEventListener('click', () => {
    history = [];
    saveHistory(); // 同步到 localStorage
    renderHistory(); // 更新视图
});

// 点击历史记录，将其加载到主显示屏
historyList.addEventListener('click', (event) => {
    const li = event.target.closest('li');
    if (!li) return;
    
    // 从 data- 属性中取回之前存的数据
    const { expr, result } = li.dataset;
    
    // 恢复当时的计算状态
    currentInput = result;
    currentExpression = ''; 
    subDisplayElement.textContent = expr + '=';
    displayElement.textContent = result;
    justCalculated = true; // 标记为“刚算完”，以便按数字时清空
});

// 切换主题
themeToggle.addEventListener('change', () => {
    if (themeToggle.checked) {
        document.body.classList.add('light-mode');
        document.body.classList.remove('dark-mode');
        // 把设置存到浏览器，下次打开还在
        localStorage.setItem('calculator-theme', 'light');
    } else {
        document.body.classList.add('dark-mode');
        document.body.classList.remove('light-mode');
        localStorage.setItem('calculator-theme', 'dark');
    }
});

// 切换标准/科学模式
modeToggle.addEventListener('change', () => {
    if (modeToggle.checked) {
        // 移除 .scientific 类，CSS 负责隐藏按钮
        calculatorElement.classList.remove('scientific');
        localStorage.setItem('calculator-mode', 'standard');
    } else {
        // 添加 .scientific 类
        calculatorElement.classList.add('scientific');
        localStorage.setItem('calculator-mode', 'scientific');
    }
});

// === 核心功能函数 ===

/**
 * 核心输入分发器
 * 所有点击和键盘输入都先经过这里
 */
function handleInput(value) {
    // 规则：如果刚算完，再按数字或 ( 或函数，就清空重来
    if (justCalculated && (/\d/.test(value) || value === '(' || prefixFunctions.includes(value) || constants.includes(value))) {
        handleClear(false); // false 表示不清空副显示屏
    }
    justCalculated = false;

    // 规则：在错误状态下，只允许 AC 或重新输入
    if (currentInput === 'Error' || currentInput === 'Infinity') {
        if (value === 'AC') handleClear();
        else if (/\d/.test(value) || value === '(' || prefixFunctions.includes(value) || constants.includes(value)) {
            handleClear();
            currentInput = value; // 开始新输入
            if (prefixFunctions.includes(value)) currentInput += '(';
        }
        else return; // 其他按键无效
    }
    
    // 根据 value 值调用不同的处理函数
    else if (prefixFunctions.includes(value)) handlePrefixFunction(value);
    else if (constants.includes(value)) handleConstant(value);
    else if (value === 'AC') handleClear();
    else if (value === 'DEL') handleDelete();
    else if (value === '=') handleEquals();
    else if (['+', '-', 'x', '/', '%', '^'].includes(value)) handleOperator(value);
    else if (value === '.') handleDecimal();
    else if (value === '(' || value === ')') handleParenthesis(value);
    else if (/\d/.test(value)) handleNumber(value);

    updateDisplay(); // 每次操作后都更新屏幕
}

/**
 * 更新主副显示屏的内容
 */
function updateDisplay() {
    displayElement.textContent = currentInput;
    subDisplayElement.textContent = currentExpression;
}

// === 输入处理子函数 ===

/**
 * 处理 sin, cos 等，自动加左括号
 */
function handlePrefixFunction(func) {
    if (currentInput === '0') {
        currentInput = func + '(';
    } else {
        currentInput += func + '(';
    }
}

/**
 * 处理 π 这样的常量
 */
function handleConstant(constValue) {
    if (currentInput === '0') {
        currentInput = constValue;
    } else {
        currentInput += constValue;
    }
}

/**
 * 处理数字输入
 */
function handleNumber(value) {
    // 如果当前是 0 或刚输入了常量，则替换
    if (currentInput === '0' || constants.includes(currentInput)) {
        currentInput = value;
    } else {
        currentInput += value;
    }
}

/**
 * 处理小数点，防止重复
 */
function handleDecimal() {
    if (!currentInput.includes('.')) {
        currentInput += '.';
    }
}

/**
 * 处理括号
 */
function handleParenthesis(value) {
    if (currentInput === '0' && value === '(') {
        currentInput = '(';
    } else {
        currentInput += value;
    }
}

/**
 * 处理 AC (全部清除)
 */
function handleClear(clearAll = true) {
    currentInput = '0';
    if (clearAll) currentExpression = ''; // 有时（如刚算完）我们不想清空表达式
    justCalculated = false;
}

/**
 * 处理 DEL (删除)
 */
function handleDelete() {
    if (currentInput.length > 1) {
        currentInput = currentInput.slice(0, -1);
    } else {
        currentInput = '0';
    }
}

/**
 * 处理运算符
 */
function handleOperator(op) {
    // 允许第一个数输入负号
    if (currentInput === '0' && currentExpression === '' && op === '-') {
        currentInput = '-';
        return;
    }

    // 把当前输入和运算符加到副屏的表达式中
    if (op === '^') {
        currentExpression += currentInput + '^';
    } else {
        currentExpression += currentInput + op;
    }
    currentInput = '0'; // 主屏归零，等待下一个数
}

/**
 * 处理 = (等于号)
 */
function handleEquals() {
    if (currentExpression === '' && currentInput === '0') return;

    // 组合表达式和当前输入，形成完整算式
    const fullExpression = currentExpression + currentInput;
    // 调用计算引擎
    const result = calculate(fullExpression);

    // 更新显示
    subDisplayElement.textContent = fullExpression + '='; 
    displayElement.textContent = result;
    
    // 保存到历史记录
    addToHistory(fullExpression, result);

    // 结果成为下一次计算的第一个数
    currentInput = String(result);
    currentExpression = '';
    justCalculated = true; // 标记为“刚算完”
}

/**
 * 真正的计算引擎
 */
function calculate(expression) {
    // 把 "x", "π", "sin(" 等替换为 JS 认识的 "Math.PI", "Math.sin("
    let safeExpression = expression
        .replace(/x/g, '*') // 乘
        .replace(/%/g, '/100') // 百分比
        .replace(/\^/g, '**') // 幂运算
        .replace(/π/g, 'Math.PI') // PI
        .replace(/√\(/g, 'Math.sqrt(') // 根号
        .replace(/sin\(/g, 'Math.sin(') // 正弦
        .replace(/cos\(/g, 'Math.cos(') // 余弦
        .replace(/tan\(/g, 'Math.tan(') // 正切
        .replace(/log\(/g, 'Math.log10(') // log
        .replace(/ln\(/g, 'Math.log('); // ln

    // 自动处理隐式乘法，比如 5(2) -> 5*(2) 或 )( -> )*(
    safeExpression = safeExpression
        .replace(/(\d)\(/g, '$1*(')
        .replace(/\)(\d)/g, ')*$1')
        .replace(/\)\(/g, ')*(');

    try {
        // 自动补全末尾的右括号
        let open = (safeExpression.match(/\(/g) || []).length;
        let close = (safeExpression.match(/\)/g) || []).length;
        if (open > close) {
            safeExpression += ')'.repeat(open - close);
        }

        // 安全版的 eval()，用来执行数学表达式
        const result = new Function('return ' + safeExpression)();

        if (!isFinite(result)) return 'Infinity'; // 处理除零
        
        // 处理 JS 浮点数精度问题 (例如 0.1 + 0.2)
        return String(parseFloat(result.toPrecision(12)));
        
    } catch (error) {
        // 捕获无效表达式 (如 "5++" 或 "sin(abc)")
        console.error("Calculation Error:", error.message, "on expression:", safeExpression);
        return 'Error';
    }
}

// === 历史记录 & 本地存储 ===

/**
 * 添加到历史数组 (内存中)
 */
function addToHistory(expression, result) {
    // 错误或无效计算不记录
    if (result === 'Error' || result === 'Infinity' || expression === result) return;
    
    const entry = { expression, result };
    history.unshift(entry); // unshift 把新纪录加到最前面

    // 限制历史记录数量
    if (history.length > 50) {
        history.pop();
    }
    
    saveHistory(); // 存到 localStorage
    renderHistory(); // 更新视图
}

/**
 * 把内存中的 history 数组渲染到 HTML 页面上
 */
function renderHistory() {
    historyList.innerHTML = ''; // 清空现有列表
    history.forEach(entry => {
        const li = document.createElement('li');
        // 把数据存回 DOM，用于点击重载
        li.dataset.expr = entry.expression;
        li.dataset.result = entry.result;
        // 插入 HTML
        li.innerHTML = `
            <span class="history-expr">${entry.expression} =</span>
            <span class="history-result">${entry.result}</span>
        `;
        historyList.appendChild(li);
    });
}

/**
 * 把 history 数组转成 JSON 字符串，存入 localStorage
 */
function saveHistory() {
    localStorage.setItem('calculator-history', JSON.stringify(history));
}

/**
 * 从 localStorage 读取 JSON 字符串，转回数组
 */
function loadHistory() {
    const storedHistory = localStorage.getItem('calculator-history');
    if (storedHistory) {
        history = JSON.parse(storedHistory);
        renderHistory(); // 渲染到页面
    }
}

/**
 * 加载主题设置
 */
function loadTheme() {
    const storedTheme = localStorage.getItem('calculator-theme');
    if (storedTheme === 'light') {
        themeToggle.checked = true;
        document.body.classList.add('light-mode');
        document.body.classList.remove('dark-mode');
    } else {
        themeToggle.checked = false;
        document.body.classList.add('dark-mode');
        document.body.classList.remove('light-mode');
    }
}

/**
 * 加载模式设置
 */
function loadMode() {
    const storedMode = localStorage.getItem('calculator-mode');
    if (storedMode === 'standard') {
        modeToggle.checked = true;
        calculatorElement.classList.remove('scientific');
    } else {
        // 默认是 scientific
        modeToggle.checked = false;
        calculatorElement.classList.add('scientific');
    }
}