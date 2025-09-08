/**
 * @file 模拟用户认证和权限数据
 * 这是前端模拟的临时方案，最终应由后端API替代。
 */

/**
 * @typedef {Object} User
 * @property {string} username - 用户名
 * @property {string} password - 密码 (明文，仅用于前端模拟)
 * @property {string} unit - 用户所属的单位名称，与menu.js中的name对应
 * @property {'super_admin' | 'regional_admin'} [globalRole] - 全局角色，拥有跨单位的特殊权限
 * @property {Object.<string, 'filler' | 'auditor'>} [rolesByProject] - 用户在各个项目中的角色
 */

/** @type {User[]} */
export const users = [
  // --- 全局与区域管理员 ---
  {
    username: 'group_admin',
    password: 'password',
    unit: '集团公司',
    globalRole: 'super_admin', // 超级管理员，可查看和修改所有内容
  },
  {
    username: 'downtown_admin',
    password: 'password',
    unit: '主城区',
    globalRole: 'regional_admin', // 区域管理员
  },

  // --- 各单位填报员 ---
  {
    username: 'beihai_filler',
    password: 'password',
    unit: '北海热电厂',
    globalRole: 'filler'
  },
  {
    username: 'xianghai_filler',
    password: 'password',
    unit: '香海热电厂',
    globalRole: 'filler'
  },
  {
    username: 'gongre_filler',
    password: 'password',
    unit: '供热公司',
    globalRole: 'filler'
  },
  {
    username: 'jinzhou_filler',
    password: 'password',
    unit: '金州热电',
    globalRole: 'filler'
  },
  {
    username: 'beifang_filler',
    password: 'password',
    unit: '北方热电',
    globalRole: 'filler'
  },
  {
    username: 'jinpu_filler',
    password: 'password',
    unit: '金普热电',
    globalRole: 'filler'
  },
  {
    username: 'zhuanghe_filler',
    password: 'password',
    unit: '庄河热电',
    globalRole: 'filler'
  },
  {
    username: 'yanjiuyuan_filler',
    password: 'password',
    unit: '研究院',
    globalRole: 'filler'
  },
];
