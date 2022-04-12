const delay = (amount = 750) =>
  new Promise(resolve => setTimeout(resolve, amount))

export async function signInRequest(data) {
  await delay()

  return {
    token: 12345789,
    user: {
      name: 'Matheus Freitas',
      email: 'matheus.freitas@linea.gov.br'
    }
  }
}

export async function recoverUserInformation() {
  await delay()

  return {
    user: {
      name: 'Matheus Freitas',
      email: 'matheus.freitas@linea.gov.br'
    }
  }
}
