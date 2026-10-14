export default function PrivacyPage() {
  return (
    <main className="container page-container narrow">
      <div className="page-intro"><span className="eyebrow">Your data</span><h1>Privacy comes first.</h1><p>Facial images are sensitive. The prototype treats image processing and long-term retention as separate decisions.</p></div>
      <div className="prose-stack">
        <section><h2>Image-check processing</h2><p>The quality-check workflow sends your chosen image directly to the configured DermaLens API. It inspects the image in memory and does not persist the raw photo. Avoid including identifying backgrounds or other people.</p></section>
        <section><h2>History and accounts</h2><p>Optional account history requires authentication with a verified identity provider and an explicit history-consent choice. History is not currently offered in this frontend until secure sign-in is configured.</p></section>
        <section><h2>Deletion and data export</h2><p>The backend includes owner-scoped data export, consent revocation and account deletion endpoints. They are only accessible with real verified authentication and a configured database.</p></section>
        <section><h2>Medical limitations</h2><p>Quality checks are not medical evaluation. The research classifier is not a validated diagnostic service. For any concerning or changing skin problem, consult a qualified healthcare professional rather than relying on a photograph classifier.</p></section>
        <section><h2>Development and third parties</h2><p>This prototype does not upload your photo to a chatbot. Project documentation may be sent to the configured RAG provider only when that feature is enabled in a later verified release.</p></section>
      </div>
    </main>
  );
}
