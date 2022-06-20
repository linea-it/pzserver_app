export default function handler(req, res) {
  // console.log(process.env.DJANGO_OAUTH_CLIENT_ID)

  const clientId = process.env.DJANGO_OAUTH_CLIENT_ID
  if (!clientId) {
    throw new Error(
      "Couldn't find environment variable: DJANGO_OAUTH_CLIENT_ID"
    )
  }
  const clientSecret = process.env.DJANGO_OAUTH_CLIENT_SECRET
  if (!clientSecret) {
    throw new Error(
      "Couldn't find environment variable: DJANGO_OAUTH_CLIENT_SECRET"
    )
  }
  res.status(200).json({
    client_id: clientId,
    client_secret: clientSecret
  })
}
