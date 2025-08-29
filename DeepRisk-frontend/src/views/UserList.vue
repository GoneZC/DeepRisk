<template>
  <div>
    <h1>用户列表</h1>
    <!-- Create -->
    <button @click="showCreateDialog">新增用户</button>

    <!-- Read -->
    <table>
      <tr v-for="user in users" :key="user.id">
        <td>{{ user.name }}</td>
        <!-- Update -->
        <td><button @click="editUser(user)">编辑</button></td>
        <!-- Delete -->
        <td><button @click="deleteUser(user.id)">删除</button></td>
      </tr>
    </table>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      users: []
    };
  },
  created() {
    this.fetchUsers();
  },
  methods: {
    async fetchUsers() {
      try {
        const response = await axios.get('http://localhost:8080/api/users');
        this.users = response.data;
      } catch (error) {
        console.error("获取用户数据失败:", error);
      }
    },
    showCreateDialog() {
      // Implementation of showCreateDialog method
    },
    editUser(user) {
      // Implementation of editUser method
    },
    deleteUser(id) {
      // Implementation of deleteUser method
    },
    async createUser() {
      try {
        await axios.post('http://localhost:8080/api/users', this.newUser);
        await this.fetchUsers();
      } catch (error) {
        console.error("创建用户失败:", error);
      }
    }
  }
};
</script> 