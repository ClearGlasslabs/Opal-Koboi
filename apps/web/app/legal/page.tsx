import Link from "next/link";

export const metadata = {
  title: "Legal, privacy and acceptable use | ClearGlassInc Artemis",
  description:
    "ClearGlassInc Artemis legal, privacy, copyright, acceptable-use and takedown templates.",
  alternates: { canonical: "/legal" },
};

export default function LegalPage() {
  return (
    <main className="legalPage">
      <Link href="/">← Return to Artemis</Link>
      <h1>Legal, privacy &amp; responsible use</h1>
      <p className="legalWarning">
        <b>Template status — legal review required.</b> Effective date: [DATE].
        Operator/legal entity: [FULL LEGAL NAME, ADDRESS, REGISTRATION]. These
        templates are not a compliance claim and must be completed for the
        actual services, data, users, vendors, and jurisdictions before
        publication.
      </p>
      <section>
        <h2>Privacy notice</h2>
        <p>
          ClearGlassInc Artemis (“we”) processes only data necessary to provide,
          secure, support, and improve the service for documented purposes.
          Controller/contact: [PRIVACY CONTACT]. Categories may include account
          and organization identifiers, authorization attributes,
          operator-submitted content, security/audit metadata, support
          communications, and consent records. Do not submit unnecessary
          sensitive or classified information.
        </p>
        <p>
          Purposes and lawful bases: [CONTRACT / LEGITIMATE INTERESTS AS
          ASSESSED / CONSENT / LEGAL OBLIGATION]. Recipients/processors and
          international transfers: [LIST AND SAFEGUARDS]. Optional analytics,
          advertising, and non-essential storage remain disabled unless
          configured with a jurisdiction-appropriate consent mechanism.
          Essential security/session storage does not track users for
          advertising.
        </p>
        <p>
          Retention: active account data for the account term plus [DAYS];
          security logs [90–365 DAYS ACCORDING TO RISK]; support records [DAYS];
          consent records [PERIOD]; backups expire within [DAYS]. Litigation
          holds and legal duties may suspend deletion. Requests for access,
          correction, deletion, portability, restriction, objection, or consent
          withdrawal: [PRIVACY EMAIL/FORM]. Identity is verified
          proportionately. Complaints may be made to [APPLICABLE AUTHORITY].
          Children/age eligibility: [AGE AND PROCESS].
        </p>
      </section>
      <section>
        <h2>Terms of use &amp; licensing</h2>
        <p>
          The service and original text, interface, graphics, software,
          provenance records, and compilations are owned by ClearGlassInc
          Artemis or its licensors. © 2026 ClearGlassInc Artemis. All rights
          reserved except rights expressly granted in a signed agreement or an
          identified open-source license. No implied license is granted.
        </p>
        <p>
          Subject to applicable law and non-waivable rights, users may not copy,
          scrape, bulk extract, republish, resell, sublicense, remove provenance
          or watermarks, circumvent access controls, or use protected content to
          train or evaluate machine-learning models without prior written
          permission. Public indexing that follows published technical and
          contractual rules may be permitted for legitimate search engines.
          These terms do not prohibit lawful security research, statutory
          exceptions, regulator access, court orders, or other non-waivable
          lawful activity.
        </p>
        <p>
          The service is provided under [GOVERNING LAW / WARRANTY / LIABILITY /
          DISPUTE TERMS APPROVED BY COUNSEL]. Technical controls reduce risk but
          do not provide absolute security, DRM, legal immunity, or prevention
          of screenshots, photography, copying, or determined extraction.
        </p>
      </section>
      <section>
        <h2>Acceptable use</h2>
        <p>
          Use must be authorized, lawful, proportionate, and consistent with
          human-rights, coalition, classification, and customer policies.
          Prohibited activity includes unauthorized access; credential theft;
          malware; harassment; unlawful surveillance or discrimination;
          destructive retaliation or hacking back; bypass of authorization,
          quotas, or approval gates; submission of material without necessary
          rights; and interference with accessibility tools or legitimate search
          indexing.
        </p>
        <p>
          Operationally significant actions require the configured human
          approvals. Suspected abuse may receive progressive, reversible
          responses: evidence-preserving logs, throttling, a proportionate
          challenge, temporary restriction, and human review. Contact
          [APPEALS/ABUSE EMAIL] to appeal.
        </p>
      </section>
      <section>
        <h2>Copyright, licensing and takedown</h2>
        <p>
          Rights holder: ClearGlassInc Artemis, [POSTAL ADDRESS], [COPYRIGHT
          EMAIL]. Permission requests must identify the work, intended use,
          territory, term, and distribution. Third-party components remain under
          their respective licenses.
        </p>
        <p>
          Notices should include claimant identity and authority, the protected
          work, exact location of disputed material, requested action, a
          good-faith statement, legally required declarations, and signature.
          Send to [DESIGNATED AGENT/EMAIL/ADDRESS]. We preserve evidence, assess
          notices and counter-notices, avoid automatic removal where
          inappropriate, and follow applicable law. Emergency or law-enforcement
          requests: [VALIDATED CHANNEL]; we do not obstruct lawful
          investigations.
        </p>
      </section>
      <section>
        <h2>Security &amp; contact</h2>
        <p>
          Report vulnerabilities through the repository’s private vulnerability
          reporting or{" "}
          <a href="mailto:security@clearglassinc.com">
            security@clearglassinc.com
          </a>
          . Do not include secrets or personal data in ordinary email. Privacy:
          [PRIVACY EMAIL]. Legal/takedown: [LEGAL EMAIL]. Accessibility
          feedback: [ACCESSIBILITY EMAIL]. General: [CONTACT EMAIL].
        </p>
      </section>
    </main>
  );
}
