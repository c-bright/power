<template>
  <div class="assistant-root">
    <div
      class="assistant-fab"
      :style="fabStyle"
      @mousedown.prevent="onMouseDown"
      @touchstart.passive="onTouchStart"
      @click="onFabClick"
      title="智能助手"
      role="button"
      aria-label="智能助手"
    >
      <i class="el-icon-chat-dot-round"></i>
    </div>

    <transition name="assistant-pop">
      <div v-show="open" class="assistant-panel" :style="panelStyle" @mousedown.stop @touchstart.stop>
        <div class="assistant-header">
          <div class="assistant-title">AI 智能助手</div>
          <button class="assistant-close" type="button" @click="open = false">×</button>
        </div>

        <div ref="msgList" class="assistant-messages">
          <div
            v-for="(m, idx) in messages"
            :key="idx"
            class="assistant-msg"
            :class="m.role"
          >
            <div class="bubble">
              <div class="text">{{ m.content }}</div>
              <div class="time" v-if="m.time">{{ m.time }}</div>
            </div>
          </div>
          <div v-if="loading" class="assistant-msg assistant">
            <div class="bubble">
              <div class="text">正在查询…</div>
            </div>
          </div>
        </div>

        <div class="assistant-quick">
          <button type="button" class="quick-btn" @click="askQuick('我的基本信息')">基本信息</button>
          <button type="button" class="quick-btn" @click="askQuick('当前计费规则和押金是多少？')">计费规则</button>
          <button type="button" class="quick-btn" @click="askQuick('查询我最近的订单/租借记录')">订单记录</button>
        </div>

        <div class="assistant-input">
          <input
            v-model.trim="input"
            class="assistant-textbox"
            type="text"
            placeholder="例如：余额还有多少？押金是多少？"
            @keydown.enter.prevent="send"
          />
          <button type="button" class="assistant-send" :disabled="loading || !input" @click="send">
            发送
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import request from '../utils/request';

const POS_STORAGE_KEY = 'assistant_fab_pos_v1';

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

export default {
  name: 'FloatingAssistant',
  data() {
    return {
      open: false,
      loading: false,
      input: '',
      messages: [],

      pos: { x: 0, y: 0 },
      dragging: false,
      moved: false,
      justDragged: false,
      dragStart: { x: 0, y: 0, posX: 0, posY: 0 }
    };
  },
  computed: {
    fabStyle() {
      return {
        left: `${this.pos.x}px`,
        top: `${this.pos.y}px`
      };
    },
    panelStyle() {
      // 面板相对悬浮按钮弹出：优先向左/向上展开，避免溢出屏幕
      const panelW = 360;
      const panelH = 480;
      const gap = 12;
      const vw = window.innerWidth || 1024;
      const vh = window.innerHeight || 768;

      const preferLeft = this.pos.x > vw / 2;
      const preferUp = this.pos.y > vh / 2;

      let left = preferLeft ? this.pos.x - panelW - gap : this.pos.x + gap;
      let top = preferUp ? this.pos.y - panelH - gap : this.pos.y + gap;

      left = clamp(left, 12, vw - panelW - 12);
      top = clamp(top, 12, vh - panelH - 12);

      return { left: `${left}px`, top: `${top}px` };
    }
  },
  mounted() {
    this.restorePos();
    window.addEventListener('resize', this.onResize, { passive: true });
    this.restoreChat();
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onResize);
    this.detachMouseListeners();
    this.detachTouchListeners();
  },
  methods: {
    restorePos() {
      const vw = window.innerWidth || 1024;
      const vh = window.innerHeight || 768;
      const radius = 28;

      const fallback = { x: vw - 72, y: vh - 140 };
      try {
        const raw = localStorage.getItem(POS_STORAGE_KEY);
        if (!raw) {
          this.pos = this.clampPos(fallback.x, fallback.y, radius);
          return;
        }
        const parsed = JSON.parse(raw);
        const x = Number(parsed.x);
        const y = Number(parsed.y);
        if (Number.isFinite(x) && Number.isFinite(y)) {
          this.pos = this.clampPos(x, y, radius);
        } else {
          this.pos = this.clampPos(fallback.x, fallback.y, radius);
        }
      } catch (e) {
        this.pos = this.clampPos(fallback.x, fallback.y, radius);
      }
    },
    persistPos() {
      try {
        localStorage.setItem(POS_STORAGE_KEY, JSON.stringify(this.pos));
      } catch (e) {
        // ignore
      }
    },
    clampPos(x, y, radius = 28) {
      const vw = window.innerWidth || 1024;
      const vh = window.innerHeight || 768;
      return {
        x: clamp(x, radius, vw - radius),
        y: clamp(y, radius, vh - radius)
      };
    },
    onResize() {
      this.pos = this.clampPos(this.pos.x, this.pos.y);
      this.persistPos();
    },

    onFabClick() {
      if (this.justDragged) return;
      this.open = !this.open;
      this.$nextTick(() => this.scrollToBottom());
    },

    // ----- Drag (Mouse) -----
    onMouseDown(e) {
      if (e.button !== 0) return;
      this.dragging = true;
      this.moved = false;
      this.dragStart = { x: e.clientX, y: e.clientY, posX: this.pos.x, posY: this.pos.y };
      this.attachMouseListeners();
    },
    attachMouseListeners() {
      window.addEventListener('mousemove', this.onMouseMove, { passive: false });
      window.addEventListener('mouseup', this.onMouseUp, { passive: true });
    },
    detachMouseListeners() {
      window.removeEventListener('mousemove', this.onMouseMove);
      window.removeEventListener('mouseup', this.onMouseUp);
    },
    onMouseMove(e) {
      if (!this.dragging) return;
      e.preventDefault();
      const dx = e.clientX - this.dragStart.x;
      const dy = e.clientY - this.dragStart.y;
      if (Math.abs(dx) + Math.abs(dy) > 3) this.moved = true;
      this.pos = this.clampPos(this.dragStart.posX + dx, this.dragStart.posY + dy);
    },
    onMouseUp() {
      if (!this.dragging) return;
      this.dragging = false;
      this.detachMouseListeners();
      this.persistPos();
      if (this.moved) {
        this.justDragged = true;
        setTimeout(() => (this.justDragged = false), 150);
      }
    },

    // ----- Drag (Touch) -----
    onTouchStart(e) {
      if (!e.touches || e.touches.length !== 1) return;
      const t = e.touches[0];
      this.dragging = true;
      this.moved = false;
      this.dragStart = { x: t.clientX, y: t.clientY, posX: this.pos.x, posY: this.pos.y };
      this.attachTouchListeners();
    },
    attachTouchListeners() {
      window.addEventListener('touchmove', this.onTouchMove, { passive: false });
      window.addEventListener('touchend', this.onTouchEnd, { passive: true });
      window.addEventListener('touchcancel', this.onTouchEnd, { passive: true });
    },
    detachTouchListeners() {
      window.removeEventListener('touchmove', this.onTouchMove);
      window.removeEventListener('touchend', this.onTouchEnd);
      window.removeEventListener('touchcancel', this.onTouchEnd);
    },
    onTouchMove(e) {
      if (!this.dragging || !e.touches || e.touches.length !== 1) return;
      e.preventDefault();
      const t = e.touches[0];
      const dx = t.clientX - this.dragStart.x;
      const dy = t.clientY - this.dragStart.y;
      if (Math.abs(dx) + Math.abs(dy) > 3) this.moved = true;
      this.pos = this.clampPos(this.dragStart.posX + dx, this.dragStart.posY + dy);
    },
    onTouchEnd() {
      if (!this.dragging) return;
      this.dragging = false;
      this.detachTouchListeners();
      this.persistPos();
      if (this.moved) {
        this.justDragged = true;
        setTimeout(() => (this.justDragged = false), 150);
      }
    },

    // ----- Chat -----
    restoreChat() {
      try {
        const raw = sessionStorage.getItem('assistant_chat_v1');
        if (!raw) return;
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) this.messages = parsed.slice(-30);
      } catch (e) {
        // ignore
      }
    },
    persistChat() {
      try {
        sessionStorage.setItem('assistant_chat_v1', JSON.stringify(this.messages.slice(-30)));
      } catch (e) {
        // ignore
      }
    },
    scrollToBottom() {
      const el = this.$refs.msgList;
      if (!el) return;
      el.scrollTop = el.scrollHeight;
    },
    askQuick(text) {
      this.open = true;
      this.input = text;
      this.$nextTick(() => this.send());
    },
    async send() {
  const question = String(this.input || '').trim();
  if (!question || this.loading) return;

  this.messages.push({
    role: 'user',
    content: question,
    time: this.formatTime(new Date())
  });

  this.input = '';
  this.persistChat();
  this.$nextTick(() => this.scrollToBottom());

  const username = localStorage.getItem('username') || '';

  if (!username) {
    this.messages.push({
      role: 'assistant',
      content: '请先登录后再使用助手哦～',
      time: this.formatTime(new Date())
    });
    return;
  }

  this.loading = true;

  // ⭐ 关键：先给一个“正在处理提示”
  const loadingMsgIndex = this.messages.push({
    role: 'assistant',
    content: '小智正在分析问题并查询数据，请稍等...',
    time: this.formatTime(new Date())
  }) - 1;

  this.$nextTick(() => this.scrollToBottom());

  try {
    const res = await request.post('/api/assistant/ask', {
      username,
      question
    });

    const data = res?.data ?? {};
    const answer =
      data?.answer ??
      data?.data?.answer ??
      data?.message ??
      '暂时没有可用回答。';

    // ⭐ 替换 loading 消息
    this.$set(this.messages, loadingMsgIndex, {
      role: 'assistant',
      content: answer,
      time: this.formatTime(new Date())
    });

  } catch (e) {
    const msg =
      e?.response?.data?.message ||
      '助手服务不可用，请稍后再试。';

    this.$set(this.messages, loadingMsgIndex, {
      role: 'assistant',
      content: msg,
      time: this.formatTime(new Date())
    });

  } finally {
    this.loading = false;
    this.persistChat();
    this.$nextTick(() => this.scrollToBottom());
  }
},
    formatTime(d) {
      const hh = String(d.getHours()).padStart(2, '0');
      const mm = String(d.getMinutes()).padStart(2, '0');
      return `${hh}:${mm}`;
    }
  }
};
</script>

<style scoped>
.assistant-root {
  position: relative;
  z-index: 3000;
}

.assistant-fab {
  position: fixed;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4a69bd, #0a74ff);
  color: #fff;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  user-select: none;
  transition: transform 0.12s ease, box-shadow 0.12s ease;
}

.assistant-fab:active {
  transform: scale(0.98);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.22);
}

.assistant-fab i {
  font-size: 22px;
}

.assistant-panel {
  position: fixed;
  width: 360px;
  height: 480px;
  border-radius: 14px;
  background: #ffffff;
  box-shadow: 0 18px 55px rgba(0, 0, 0, 0.22);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.assistant-header {
  height: 48px;
  background: #f7f9fc;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
}

.assistant-title {
  font-weight: 700;
  color: #1f2d3d;
  font-size: 14px;
}

.assistant-close {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 18px;
  line-height: 28px;
  color: #606266;
}

.assistant-messages {
  flex: 1;
  padding: 12px;
  overflow: auto;
  background: #ffffff;
}

.assistant-msg {
  display: flex;
  margin-bottom: 10px;
}

.assistant-msg.user {
  justify-content: flex-end;
}

.assistant-msg.assistant {
  justify-content: flex-start;
}

.bubble {
  max-width: 78%;
  padding: 10px 12px;
  border-radius: 12px;
  line-height: 1.5;
  font-size: 13px;
  word-break: break-word;
}

.assistant-msg.user .bubble {
  background: #4a69bd;
  color: #fff;
  border-bottom-right-radius: 6px;
}

.assistant-msg.assistant .bubble {
  background: #f2f4f7;
  color: #303133;
  border-bottom-left-radius: 6px;
}

.time {
  margin-top: 6px;
  font-size: 11px;
  opacity: 0.65;
}

.assistant-quick {
  padding: 10px 12px 0;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  background: #fff;
}

.quick-btn {
  border: 1px solid rgba(74, 105, 189, 0.28);
  background: rgba(74, 105, 189, 0.06);
  color: #2c3e50;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 12px;
  cursor: pointer;
}

.quick-btn:hover {
  background: rgba(74, 105, 189, 0.12);
}

.assistant-input {
  display: flex;
  gap: 8px;
  padding: 10px 12px 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  background: #fff;
}

.assistant-textbox {
  flex: 1;
  height: 36px;
  border-radius: 10px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  padding: 0 10px;
  font-size: 13px;
  outline: none;
}

.assistant-textbox:focus {
  border-color: rgba(74, 105, 189, 0.55);
  box-shadow: 0 0 0 3px rgba(74, 105, 189, 0.12);
}

.assistant-send {
  height: 36px;
  padding: 0 12px;
  border: none;
  border-radius: 10px;
  background: #0a74ff;
  color: #fff;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
}

.assistant-send:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.assistant-pop-enter-active,
.assistant-pop-leave-active {
  transition: opacity 0.16s ease, transform 0.16s ease;
}
.assistant-pop-enter,
.assistant-pop-leave-to {
  opacity: 0;
  transform: translateY(6px) scale(0.985);
}
</style>

