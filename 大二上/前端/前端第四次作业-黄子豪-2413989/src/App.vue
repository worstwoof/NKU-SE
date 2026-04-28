<script setup>
import { ref, computed } from 'vue';

const inputValue = ref(''); 
const todoList = ref([]);

const today = new Date().toLocaleDateString('zh-CN', { 
  weekday: 'long', 
  year: 'numeric', 
  month: 'long', 
  day: 'numeric' 
});

const handleAdd = () => {
  if (!inputValue.value.trim()) return;
  
  todoList.value.unshift({
    id: Date.now(),
    content: inputValue.value,
    date: '刚刚'
  });
  inputValue.value = '';
};

const handleDelete = (id) => {
  todoList.value = todoList.value.filter(item => item.id !== id);
};

const handleClearAll = () => {
  if(todoList.value.length === 0) return;
  if (confirm('确认清空所有任务清单吗？')) {
    todoList.value = [];
  }
};

const totalTasks = computed(() => todoList.value.length);
</script>

<template>
  <div class="fullscreen-container">
    
    <div class="glass-dashboard">
      
      <header class="dashboard-header">
        <div class="header-left">
          <h1 class="app-title">Workplace Todo</h1>
          <p class="current-date">{{ today }}</p>
        </div>
        <div class="header-right">
          <span class="task-counter">待办任务: <strong>{{ totalTasks }}</strong></span>
        </div>
      </header>

      <main class="main-content">
        
        <div class="input-wrapper">
          <input 
            v-model="inputValue" 
            type="text" 
            placeholder="今天想做点什么？(回车快速添加)" 
            class="premium-input"
            @keyup.enter="handleAdd" 
          />
          <button class="btn-gradient-add" @click="handleAdd">
            <span>+ 新建任务</span>
          </button>
        </div>

        <div class="list-scroll-area">
          <transition-group name="list" tag="ul" class="task-list">
            <li v-for="item in todoList" :key="item.id" class="task-card">
              <div class="card-content">
                <span class="task-text">{{ item.content }}</span>
                <span class="task-tag">{{ item.date }}</span>
              </div>
              <button class="btn-icon-delete" @click="handleDelete(item.id)" title="删除">
                ✕
              </button>
            </li>
          </transition-group>

          <div v-if="todoList.length === 0" class="empty-state">
            <div class="empty-icon">🎉</div>
            <p>太棒了！所有任务已完成</p>
          </div>
        </div>
      </main>

      <footer class="dashboard-footer">
        <button class="btn-text-clear" @click="handleClearAll">清空列表</button>
      </footer>
    </div>
  </div>
</template>

<style>
:root, body, #app {
  margin: 0 !important;
  padding: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  max-width: 100vw !important;
  overflow: hidden !important;
  display: block !important;
}
</style>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

.fullscreen-container {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: 'Inter', 'PingFang SC', sans-serif;
}

.glass-dashboard {
  width: 90%;
  max-width: 1400px;
  height: 90vh;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(255, 255, 255, 0.18);
  padding: 40px;
  box-sizing: border-box;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(0,0,0,0.05);
}

.app-title {
  font-size: 36px;
  color: #1a202c;
  margin: 0;
  font-weight: 800;
  letter-spacing: -1px;
}

.current-date {
  color: #718096;
  margin: 5px 0 0 0;
  font-size: 16px;
}

.task-counter {
  font-size: 18px;
  color: #4a5568;
  background: white;
  padding: 8px 16px;
  border-radius: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.input-wrapper {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.premium-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.6);
  border: 2px solid transparent;
  padding: 16px 24px;
  border-radius: 16px;
  font-size: 18px;
  color: #2d3748;
  transition: all 0.3s ease;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
}

.premium-input:focus {
  outline: none;
  background: white;
  border-color: #764ba2;
  box-shadow: 0 0 0 4px rgba(118, 75, 162, 0.2);
}

.btn-gradient-add {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 0 32px;
  border-radius: 16px;
  color: white;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  white-space: nowrap;
}

.btn-gradient-add:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(118, 75, 162, 0.4);
}

.list-scroll-area {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
}

.list-scroll-area::-webkit-scrollbar {
  width: 8px;
}
.list-scroll-area::-webkit-scrollbar-thumb {
  background-color: rgba(0,0,0,0.1);
  border-radius: 4px;
}

.task-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.task-card {
  background: white;
  padding: 20px 24px;
  border-radius: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 6px rgba(0,0,0,0.02);
  border: 1px solid rgba(0,0,0,0.02);
  transition: all 0.2s ease;
}

.task-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 15px rgba(0,0,0,0.05);
  border-color: #e2e8f0;
}

.card-content {
  display: flex;
  flex-direction: column;
}

.task-text {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
}

.task-tag {
  font-size: 12px;
  color: #a0aec0;
  margin-top: 4px;
  font-weight: 600;
  text-transform: uppercase;
}

.btn-icon-delete {
  background: transparent;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  color: #cbd5e0;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon-delete:hover {
  background-color: #fff5f5;
  color: #e53e3e;
}

.dashboard-footer {
  margin-top: 20px;
  text-align: right;
  border-top: 1px solid rgba(0,0,0,0.05);
  padding-top: 20px;
}

.btn-text-clear {
  background: none;
  border: none;
  color: #718096;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s;
}

.btn-text-clear:hover {
  color: #e53e3e;
  text-decoration: underline;
}

.list-enter-active,
.list-leave-active {
  transition: all 0.4s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.empty-state {
  text-align: center;
  margin-top: 50px;
  color: #a0aec0;
}
.empty-icon {
  font-size: 48px;
  margin-bottom: 10px;
}
</style>