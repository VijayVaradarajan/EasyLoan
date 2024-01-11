import config from '@/utils/config';


let api_host = `/v1`;


export { api_host };

export default {
  icp: config.COPY_RIGHT_TEXT,

  upload: `${api_host}/upload`,
  uploadZip: `${api_host}/uploadZip`,
  segment_upload: `${api_host}/uploadPopulation`,

  // 用户
  login: `${api_host}/user/login`,
  register: `${api_host}/user/register`,
  user: `${api_host}/user/validate`,
  getUrl: `${api_host}/requestGetUrl`,
  getAdPermits: `${api_host}/adServer/getAdPermits`,

  //子用户管理
  account_list: `${api_host}/user/getUserList`,
  create_account: `${api_host}/user/createUserAccountSso`,
  update_account: `${api_host}/user/updateUserAccountSso`,
  account_detail: `${api_host}/user/getUserDetail`,
  getUserDetail: `${api_host}/user/getUserDetail`,
  account_status: `${api_host}/user/updateAccountStatus`,
  sign_agreement: `${api_host}/user/updateUserSignAgreement`,

};
