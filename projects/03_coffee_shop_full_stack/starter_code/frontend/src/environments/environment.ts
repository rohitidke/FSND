/*
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-matrix.us.auth0.com', // the auth0 domain prefix
    audience: 'coffee', // the audience set for the auth0 app
    clientId: '1euVv14hZhO3dl11iCRLFf26vao5NuzK', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
