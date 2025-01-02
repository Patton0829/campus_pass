<template>
  <div class="federal-learning-ai-assistant-component">
    <h2>理工大教师信息助手</h2>
    <input
      v-model="userQuestion"
      placeholder="请输入您的问题"
      class="question-input"
    />
    <button @click="sendRequest" class="send-button">发送请求</button>
    <div v-if="loading" class="loading-wrapper">
      <p>正在向AI助手请求，请稍等...</p>
    </div>
    <div v-if="responseData" class="response-wrapper">
      <h3>AI助手的回答：</h3>
      <p class="response-content">{{ responseData }}</p>
    </div>
    <div v-if="errorMsg" class="error-wrapper">
      <p class="error-content">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      userQuestion: "",
      loading: false,
      responseData: null,
      errorMsg: "",
    };
  },
  methods: {
    async sendRequest() {
      this.loading = true;
      this.errorMsg = "";
      try {
        const response = await axios.post('http://localhost:8000', {
      input: {
        question: this.userQuestion
      },
      config: {},
      kwargs: {}
    }, {
      headers: {
        'accept': 'application/json',
        'Content-Type': 'application/json'
      },
      params: {
        question: this.userQuestion
      }
    });
        console.log(response)
        this.responseData = response.data;
        console.log(this.responseData)
      } catch (error) {
        if (error.response) {
          if (error.response.status === 400) {
            this.errorMsg = "请求参数有误，请检查输入内容。";
          } else if (error.response.status === 404) {
            this.errorMsg = "请求的接口路径不存在，请检查接口地址是否正确。";
          } else if (error.response.status === 500) {
            this.errorMsg = "AI助手服务内部出现错误，请稍后再试。";
          } else {
            this.errorMsg = `请求出现错误，状态码：${error.response.status}`;
          }
        } else if (error.request) {
          this.errorMsg = "请求未收到响应，请检查网络连接。";
        } else {
          this.errorMsg = "请求配置出现问题，请联系管理员。";
        }
        console.error("请求AI助手应用出错：", error);
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.federal-learning-ai-assistant-component {
  width: 600px;
  margin: 50px auto;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  background-color: #f9f9f9;
}

.question-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 16px;
  margin-bottom: 20px;
}

.send-button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.send-button:hover {
  background-color: #0056b3;
}

.loading-wrapper {
  margin-top: 20px;
  text-align: center;
}

.response-wrapper {
  margin-top: 20px;
  padding: 15px;
  border-radius: 5px;
  background-color: #e6f7ff;
}

.response-content {
  color: #333;
  font-size: 16px;
  line-height: 1.6;
}

.error-wrapper {
  margin-top: 20px;
  padding: 15px;
  border-radius: 5px;
  background-color: #ffe6e6;
}

.error-content {
  color: #ff0000;
  font-size: 16px;
  line-height: 1.6;
}
</style>