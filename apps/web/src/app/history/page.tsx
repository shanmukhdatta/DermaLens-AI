import { identity, identityConfigured } from "@/auth";
import HistoryWorkspace from "./history-workspace";

export const dynamic = "force-dynamic";

export default async function HistoryPage() {
  const session = identity ? await identity.auth() : null;
  return <main className="container page-container">
    <div className="page-intro">
      <span className="eyebrow">Protected workspace</span>
      <h1>Your private analysis history.</h1>
      <p>Secure sign-in and consent are required. Face images are never stored by this application.</p>
    </div>
    {!identityConfigured && <section className="card">
      <h2>Sign-in provider not configured</h2>
      <p>This deployment has no OIDC identity provider. Research history and private uploads
         remain unavailable; no sample medical results are displayed.</p>
    </section>}
    {identityConfigured && !session && <section className="card">
      <h2>Sign in to continue</h2>
      <form action={async () => {
        "use server";
        if (identity) await identity.signIn("dermalens-oidc");
      }}>
        <button className="button" type="submit">Sign in securely</button>
      </form>
    </section>}
    {session && <><form action={async () => {
      "use server";
      if (identity) await identity.signOut({ redirectTo: "/history" });
    }}><button className="button button-outline" type="submit">Sign out</button></form>
    <HistoryWorkspace /></>}
  </main>;
}
