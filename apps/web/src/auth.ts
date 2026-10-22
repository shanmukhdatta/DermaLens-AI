import NextAuth from "next-auth";

const issuer = process.env.DERMALENS_WEB_OIDC_ISSUER;
const clientId = process.env.DERMALENS_WEB_OIDC_CLIENT_ID;
const clientSecret = process.env.DERMALENS_WEB_OIDC_CLIENT_SECRET;
const sessionSecret = process.env.AUTH_SECRET;

export const identityConfigured = Boolean(issuer && clientId && clientSecret && sessionSecret);

// No provider or fake development login is created when configuration is absent.
export const identity = identityConfigured ? NextAuth({
  secret: sessionSecret,
  trustHost: false,
  session: { strategy: "jwt", maxAge: 60 * 60 },
  providers: [{
    id: "dermalens-oidc",
    name: "Secure identity provider",
    type: "oidc",
    issuer: issuer!,
    clientId: clientId!,
    clientSecret: clientSecret!,
    authorization: { params: { scope: "openid profile email" } },
    checks: ["pkce", "state"],
  }],
  callbacks: {
    async jwt({ token, account }) {
      // Encrypted server-session JWT only; never include this field in
      // the public session callback or frontend React properties.
      if (account?.access_token && account.expires_at) {
        token.apiBearer = account.access_token;
        token.apiBearerExpiry = account.expires_at;
      }
      return token;
    },
    async session({ session }) {
      return session; // deliberately excludes raw provider bearer token
    },
  },
}) : null;
