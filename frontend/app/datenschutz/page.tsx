import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Datenschutzerklärung | LinkedIn Christmas Code Challenge',
  description: 'Datenschutzerklärung und Informationen zur Datenverarbeitung',
};

export default function Datenschutz() {
  return (
    <main className="min-h-screen p-4 md:p-8 flex flex-col items-center relative z-10">
      {/* Back Navigation */}
      <div className="w-full max-w-4xl mb-6">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-terminal-green/70 hover:text-terminal-green transition-colors duration-200 text-sm"
        >
          <span>←</span>
          <span>Zurück zur Challenge</span>
        </Link>
      </div>

      {/* Terminal Window */}
      <div className="w-full max-w-4xl terminal-window">
        {/* Terminal Header */}
        <div className="terminal-header">
          <div className="terminal-dot red" />
          <div className="terminal-dot yellow" />
          <div className="terminal-dot green" />
          <span className="ml-4 text-sm opacity-50">
            🔒 cat /legal/datenschutz.txt
          </span>
        </div>

        {/* Content */}
        <div className="p-6 md:p-8 space-y-8 text-sm md:text-base leading-relaxed">
          {/* Title */}
          <div className="text-center mb-8">
            <h1 className="text-2xl md:text-3xl font-bold text-[#ffd700] glow-text-gold font-['Orbitron'] mb-2">
              DATENSCHUTZERKLÄRUNG
            </h1>
            <div className="h-px w-32 mx-auto bg-gradient-to-r from-transparent via-terminal-green to-transparent" />
          </div>

          {/* 1. Datenschutz auf einen Blick */}
          <section>
            <h2 className="text-xl text-terminal-cyan font-semibold mb-4">{'>'} 1. Datenschutz auf einen Blick</h2>
            
            <h3 className="text-terminal-amber font-semibold mb-2">Allgemeine Hinweise</h3>
            <p className="text-terminal-green/80 mb-4">
              Die folgenden Hinweise geben einen einfachen Überblick darüber, was mit Ihren personenbezogenen
              Daten passiert, wenn Sie diese Website besuchen. Personenbezogene Daten sind alle Daten, mit
              denen Sie persönlich identifiziert werden können. Ausführliche Informationen zum Thema
              Datenschutz entnehmen Sie unserer unter diesem Text aufgeführten Datenschutzerklärung.
            </p>

            <h3 className="text-terminal-amber font-semibold mb-2">Datenerfassung auf dieser Website</h3>
            <p className="text-terminal-green/70 italic mb-2">Wer ist verantwortlich für die Datenerfassung auf dieser Website?</p>
            <p className="text-terminal-green/80 mb-4">
              Die Datenverarbeitung auf dieser Website erfolgt durch den Websitebetreiber. Dessen
              Kontaktdaten können Sie dem Abschnitt „Hinweis zur Verantwortlichen Stelle" in dieser
              Datenschutzerklärung entnehmen.
            </p>

            <p className="text-terminal-green/70 italic mb-2">Wie erfassen wir Ihre Daten?</p>
            <p className="text-terminal-green/80 mb-2">
              Ihre Daten werden zum einen dadurch erhoben, dass Sie uns diese mitteilen. Hierbei kann es
              sich z. B. um Daten handeln, die Sie in ein Kontaktformular eingeben.
            </p>
            <p className="text-terminal-green/80 mb-4">
              Andere Daten werden automatisch oder nach Ihrer Einwilligung beim Besuch der Website durch
              unsere IT-Systeme erfasst. Das sind vor allem technische Daten (z. B. Internetbrowser,
              Betriebssystem oder Uhrzeit des Seitenaufrufs). Die Erfassung dieser Daten erfolgt
              automatisch, sobald Sie diese Website betreten.
            </p>

            <p className="text-terminal-green/70 italic mb-2">Wofür nutzen wir Ihre Daten?</p>
            <p className="text-terminal-green/80 mb-4">
              Ein Teil der Daten wird erhoben, um eine fehlerfreie Bereitstellung der Website zu
              gewährleisten. Andere Daten können zur Analyse Ihres Nutzerverhaltens verwendet werden.
              Sofern über die Website Verträge geschlossen oder angebahnt werden können, werden die
              übermittelten Daten auch für Vertragsangebote, Bestellungen oder sonstige Auftragsanfragen
              verarbeitet.
            </p>

            <p className="text-terminal-green/70 italic mb-2">Welche Rechte haben Sie bezüglich Ihrer Daten?</p>
            <p className="text-terminal-green/80 mb-4">
              Sie haben jederzeit das Recht, unentgeltlich Auskunft über Herkunft, Empfänger und Zweck
              Ihrer gespeicherten personenbezogenen Daten zu erhalten. Sie haben außerdem ein Recht, die
              Berichtigung oder Löschung dieser Daten zu verlangen. Wenn Sie eine Einwilligung zur
              Datenverarbeitung erteilt haben, können Sie diese Einwilligung jederzeit für die Zukunft
              widerrufen. Außerdem haben Sie das Recht, unter bestimmten Umständen die Einschränkung der
              Verarbeitung Ihrer personenbezogenen Daten zu verlangen. Des Weiteren steht Ihnen ein
              Beschwerderecht bei der zuständigen Aufsichtsbehörde zu.
            </p>
            <p className="text-terminal-green/80 mb-4">
              Hierzu sowie zu weiteren Fragen zum Thema Datenschutz können Sie sich jederzeit an uns wenden.
            </p>

            <h3 className="text-terminal-amber font-semibold mb-2">Analyse-Tools und Tools von Drittanbietern</h3>
            <p className="text-terminal-green/80 mb-4">
              Beim Besuch dieser Website kann Ihr Surf-Verhalten statistisch ausgewertet werden. Das
              geschieht vor allem mit sogenannten Analyseprogrammen. Detaillierte Informationen zu diesen
              Analyseprogrammen finden Sie in der folgenden Datenschutzerklärung.
            </p>
          </section>

          {/* 2. Hosting */}
          <section>
            <h2 className="text-xl text-terminal-cyan font-semibold mb-4">{'>'} 2. Hosting</h2>
            <p className="text-terminal-green/80 mb-2">
              Wir hosten die Inhalte unserer Website bei folgendem Anbieter:
            </p>
            <h3 className="text-terminal-amber font-semibold mb-2">IONOS</h3>
            <p className="text-terminal-green/80 mb-4">
              Anbieter ist die IONOS SE, Elgendorfer Str. 57, 56410 Montabaur (nachfolgend IONOS). Wenn
              Sie unsere Website besuchen, erfasst IONOS verschiedene Logfiles inklusive Ihrer IP-Adressen.
              Details entnehmen Sie der Datenschutzerklärung von IONOS:{' '}
              <a
                href="https://www.ionos.de/terms-gtc/terms-privacy"
                target="_blank"
                rel="noopener noreferrer"
                className="text-terminal-amber hover:glow-text-gold transition-all duration-200 break-all"
              >
                https://www.ionos.de/terms-gtc/terms-privacy
              </a>
            </p>
            <p className="text-terminal-green/80 mb-4">
              Die Verwendung von IONOS erfolgt auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO. Wir haben ein
              berechtigtes Interesse an einer möglichst zuverlässigen Darstellung unserer Website. Sofern
              eine entsprechende Einwilligung abgefragt wurde, erfolgt die Verarbeitung ausschließlich auf
              Grundlage von Art. 6 Abs. 1 lit. a DSGVO und § 25 Abs. 1 TDDDG, soweit die Einwilligung die
              Speicherung von Cookies oder den Zugriff auf Informationen im Endgerät des Nutzers (z. B.
              Device-Fingerprinting) im Sinne des TDDDG umfasst. Die Einwilligung ist jederzeit widerrufbar.
            </p>
            <h3 className="text-terminal-amber font-semibold mb-2">Auftragsverarbeitung</h3>
            <p className="text-terminal-green/80 mb-4">
              Wir haben einen Vertrag über Auftragsverarbeitung (AVV) zur Nutzung des oben genannten
              Dienstes geschlossen. Hierbei handelt es sich um einen datenschutzrechtlich vorgeschriebenen
              Vertrag, der gewährleistet, dass dieser die personenbezogenen Daten unserer Websitebesucher
              nur nach unseren Weisungen und unter Einhaltung der DSGVO verarbeitet.
            </p>
          </section>

          {/* 3. Allgemeine Hinweise */}
          <section>
            <h2 className="text-xl text-terminal-cyan font-semibold mb-4">{'>'} 3. Allgemeine Hinweise und Pflichtinformationen</h2>
            
            <h3 className="text-terminal-amber font-semibold mb-2">Datenschutz</h3>
            <p className="text-terminal-green/80 mb-4">
              Die Betreiber dieser Seiten nehmen den Schutz Ihrer persönlichen Daten sehr ernst. Wir
              behandeln Ihre personenbezogenen Daten vertraulich und entsprechend den gesetzlichen
              Datenschutzvorschriften sowie dieser Datenschutzerklärung. Wenn Sie diese Website benutzen,
              werden verschiedene personenbezogene Daten erhoben. Die vorliegende Datenschutzerklärung
              erläutert, welche Daten wir erheben und wofür wir sie nutzen. Wir weisen darauf hin, dass
              die Datenübertragung im Internet Sicherheitslücken aufweisen kann. Ein lückenloser Schutz
              der Daten vor dem Zugriff durch Dritte ist nicht möglich.
            </p>

            <h3 className="text-terminal-amber font-semibold mb-2">Hinweis zur verantwortlichen Stelle</h3>
            <p className="text-terminal-green/80 mb-2">
              Die verantwortliche Stelle für die Datenverarbeitung auf dieser Website ist:
            </p>
            <div className="bg-terminal-bg/50 p-4 rounded border border-terminal-green/20 mb-4">
              <p className="text-terminal-green">Stefan Müller</p>
              <p className="text-terminal-green/80">Graeffstr. 22</p>
              <p className="text-terminal-green/80">50823 Köln</p>
              <p className="text-terminal-green/80 mt-2">Telefon: 0221/5702984</p>
              <p className="text-terminal-green/80">
                E-Mail:{' '}
                <a
                  href="mailto:info@stefanai.de"
                  className="text-terminal-green hover:glow-text transition-all duration-200"
                >
                  info@stefanai.de
                </a>
              </p>
            </div>
            <p className="text-terminal-green/80 mb-4">
              Verantwortliche Stelle ist die natürliche oder juristische Person, die allein oder gemeinsam
              mit anderen über die Zwecke und Mittel der Verarbeitung von personenbezogenen Daten
              entscheidet.
            </p>

            <h3 className="text-terminal-amber font-semibold mb-2">Speicherdauer</h3>
            <p className="text-terminal-green/80 mb-4">
              Soweit innerhalb dieser Datenschutzerklärung keine speziellere Speicherdauer genannt wurde,
              verbleiben Ihre personenbezogenen Daten bei uns, bis der Zweck für die Datenverarbeitung
              entfällt. Wenn Sie ein berechtigtes Löschersuchen geltend machen oder eine Einwilligung zur
              Datenverarbeitung widerrufen, werden Ihre Daten gelöscht, sofern wir keine anderen rechtlich
              zulässigen Gründe für die Speicherung Ihrer personenbezogenen Daten haben.
            </p>

            <h3 className="text-terminal-amber font-semibold mb-2">Allgemeine Hinweise zu den Rechtsgrundlagen</h3>
            <p className="text-terminal-green/80 mb-4">
              Sofern Sie in die Datenverarbeitung eingewilligt haben, verarbeiten wir Ihre
              personenbezogenen Daten auf Grundlage von Art. 6 Abs. 1 lit. a DSGVO bzw. Art. 9 Abs. 2
              lit. a DSGVO. Sind Ihre Daten zur Vertragserfüllung oder zur Durchführung vorvertraglicher
              Maßnahmen erforderlich, verarbeiten wir Ihre Daten auf Grundlage des Art. 6 Abs. 1 lit. b
              DSGVO. Des Weiteren verarbeiten wir Ihre Daten, sofern diese zur Erfüllung einer rechtlichen
              Verpflichtung erforderlich sind auf Grundlage von Art. 6 Abs. 1 lit. c DSGVO.
            </p>

            <h3 className="text-terminal-amber font-semibold mb-2">Empfänger von personenbezogenen Daten</h3>
            <p className="text-terminal-green/80 mb-4">
              Im Rahmen unserer Geschäftstätigkeit arbeiten wir mit verschiedenen externen Stellen
              zusammen. Wir geben personenbezogene Daten nur dann an externe Stellen weiter, wenn dies im
              Rahmen einer Vertragserfüllung erforderlich ist, wenn wir gesetzlich hierzu verpflichtet
              sind, wenn wir ein berechtigtes Interesse haben oder wenn eine sonstige Rechtsgrundlage die
              Datenweitergabe erlaubt.
            </p>

            <h3 className="text-terminal-amber font-semibold mb-2">Widerruf Ihrer Einwilligung zur Datenverarbeitung</h3>
            <p className="text-terminal-green/80 mb-4">
              Viele Datenverarbeitungsvorgänge sind nur mit Ihrer ausdrücklichen Einwilligung möglich. Sie
              können eine bereits erteilte Einwilligung jederzeit widerrufen. Die Rechtmäßigkeit der bis
              zum Widerruf erfolgten Datenverarbeitung bleibt vom Widerruf unberührt.
            </p>

            <h3 className="text-terminal-amber font-semibold mb-2">Widerspruchsrecht (Art. 21 DSGVO)</h3>
            <div className="bg-christmas-red/10 border border-christmas-red/30 p-4 rounded mb-4">
              <p className="text-terminal-green/90 uppercase text-xs leading-relaxed">
                Wenn die Datenverarbeitung auf Grundlage von Art. 6 Abs. 1 lit. E oder F DSGVO erfolgt,
                haben Sie jederzeit das Recht, aus Gründen, die sich aus Ihrer besonderen Situation
                ergeben, gegen die Verarbeitung Ihrer personenbezogenen Daten Widerspruch einzulegen.
                Werden Ihre personenbezogenen Daten verarbeitet, um Direktwerbung zu betreiben, so haben
                Sie das Recht, jederzeit Widerspruch gegen die Verarbeitung einzulegen.
              </p>
            </div>

            <h3 className="text-terminal-amber font-semibold mb-2">Beschwerderecht bei der zuständigen Aufsichtsbehörde</h3>
            <p className="text-terminal-green/80 mb-4">
              Im Falle von Verstößen gegen die DSGVO steht den Betroffenen ein Beschwerderecht bei einer
              Aufsichtsbehörde zu, insbesondere in dem Mitgliedstaat ihres gewöhnlichen Aufenthalts, ihres
              Arbeitsplatzes oder des Orts des mutmaßlichen Verstoßes.
            </p>

            <h3 className="text-terminal-amber font-semibold mb-2">Recht auf Datenübertragbarkeit</h3>
            <p className="text-terminal-green/80 mb-4">
              Sie haben das Recht, Daten, die wir auf Grundlage Ihrer Einwilligung oder in Erfüllung eines
              Vertrags automatisiert verarbeiten, an sich oder an einen Dritten in einem gängigen,
              maschinenlesbaren Format aushändigen zu lassen.
            </p>

            <h3 className="text-terminal-amber font-semibold mb-2">Auskunft, Berichtigung und Löschung</h3>
            <p className="text-terminal-green/80 mb-4">
              Sie haben im Rahmen der geltenden gesetzlichen Bestimmungen jederzeit das Recht auf
              unentgeltliche Auskunft über Ihre gespeicherten personenbezogenen Daten, deren Herkunft und
              Empfänger und den Zweck der Datenverarbeitung und ggf. ein Recht auf Berichtigung oder
              Löschung dieser Daten.
            </p>

            <h3 className="text-terminal-amber font-semibold mb-2">Recht auf Einschränkung der Verarbeitung</h3>
            <p className="text-terminal-green/80 mb-4">
              Sie haben das Recht, die Einschränkung der Verarbeitung Ihrer personenbezogenen Daten zu
              verlangen in folgenden Fällen: wenn Sie die Richtigkeit bestreiten, wenn die Verarbeitung
              unrechtmäßig ist, wenn wir die Daten nicht mehr benötigen Sie sie aber für Rechtsansprüche
              benötigen, oder wenn Sie Widerspruch eingelegt haben.
            </p>

            <h3 className="text-terminal-amber font-semibold mb-2">SSL- bzw. TLS-Verschlüsselung</h3>
            <p className="text-terminal-green/80 mb-4">
              Diese Seite nutzt aus Sicherheitsgründen und zum Schutz der Übertragung vertraulicher
              Inhalte eine SSL- bzw. TLS-Verschlüsselung. Eine verschlüsselte Verbindung erkennen Sie
              daran, dass die Adresszeile des Browsers von „http://" auf „https://" wechselt und an dem
              Schloss-Symbol in Ihrer Browserzeile.
            </p>
          </section>

          {/* 4. Datenerfassung auf dieser Website */}
          <section>
            <h2 className="text-xl text-terminal-cyan font-semibold mb-4">{'>'} 4. Datenerfassung auf dieser Website</h2>

            <h3 className="text-terminal-amber font-semibold mb-2">Cookies</h3>
            <p className="text-terminal-green/80 mb-4">
              Unsere Internetseiten verwenden so genannte „Cookies". Cookies sind kleine Datenpakete und
              richten auf Ihrem Endgerät keinen Schaden an. Sie werden entweder vorübergehend für die
              Dauer einer Sitzung (Session-Cookies) oder dauerhaft (permanente Cookies) auf Ihrem Endgerät
              gespeichert. Session-Cookies werden nach Ende Ihres Besuchs automatisch gelöscht. Permanente
              Cookies bleiben auf Ihrem Endgerät gespeichert, bis Sie diese selbst löschen oder eine
              automatische Löschung durch Ihren Webbrowser erfolgt.
            </p>
            <p className="text-terminal-green/80 mb-4">
              Cookies, die zur Durchführung des elektronischen Kommunikationsvorgangs oder zur
              Bereitstellung bestimmter, von Ihnen erwünschter Funktionen erforderlich sind, werden auf
              Grundlage von Art. 6 Abs. 1 lit. f DSGVO gespeichert. Sie können Ihren Browser so einstellen,
              dass Sie über das Setzen von Cookies informiert werden und Cookies nur im Einzelfall erlauben.
            </p>

            <h3 className="text-terminal-amber font-semibold mb-2">Server-Log-Dateien</h3>
            <p className="text-terminal-green/80 mb-2">
              Der Provider der Seiten erhebt und speichert automatisch Informationen in so genannten
              Server-Log-Dateien, die Ihr Browser automatisch an uns übermittelt. Dies sind:
            </p>
            <ul className="list-none space-y-1 mb-4 pl-4">
              <li className="text-terminal-green/80">• Browsertyp und Browserversion</li>
              <li className="text-terminal-green/80">• verwendetes Betriebssystem</li>
              <li className="text-terminal-green/80">• Referrer URL</li>
              <li className="text-terminal-green/80">• Hostname des zugreifenden Rechners</li>
              <li className="text-terminal-green/80">• Uhrzeit der Serveranfrage</li>
              <li className="text-terminal-green/80">• IP-Adresse</li>
            </ul>
            <p className="text-terminal-green/80 mb-4">
              Eine Zusammenführung dieser Daten mit anderen Datenquellen wird nicht vorgenommen. Die
              Erfassung dieser Daten erfolgt auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO.
            </p>

            <h3 className="text-terminal-amber font-semibold mb-2">Kontaktformular</h3>
            <p className="text-terminal-green/80 mb-4">
              Wenn Sie uns per Kontaktformular Anfragen zukommen lassen, werden Ihre Angaben aus dem
              Anfrageformular inklusive der von Ihnen dort angegebenen Kontaktdaten zwecks Bearbeitung der
              Anfrage und für den Fall von Anschlussfragen bei uns gespeichert. Diese Daten geben wir
              nicht ohne Ihre Einwilligung weiter.
            </p>

            <h3 className="text-terminal-amber font-semibold mb-2">Anfrage per E-Mail, Telefon oder Telefax</h3>
            <p className="text-terminal-green/80 mb-4">
              Wenn Sie uns per E-Mail, Telefon oder Telefax kontaktieren, wird Ihre Anfrage inklusive
              aller daraus hervorgehenden personenbezogenen Daten zum Zwecke der Bearbeitung Ihres
              Anliegens bei uns gespeichert und verarbeitet. Diese Daten geben wir nicht ohne Ihre
              Einwilligung weiter.
            </p>

            <h3 className="text-terminal-amber font-semibold mb-2">Calendly</h3>
            <p className="text-terminal-green/80 mb-4">
              Auf unserer Website haben Sie die Möglichkeit, Termine mit uns zu vereinbaren. Für die
              Terminbuchung nutzen wir das Tool „Calendly" (Calendly LLC, 271 17th St NW, 10th Floor,
              Atlanta, Georgia 30363, USA). Die eingegebenen Daten werden für die Planung, Durchführung
              und ggf. für die Nachbereitung des Termins verwendet. Details finden Sie unter:{' '}
              <a
                href="https://calendly.com/privacy"
                target="_blank"
                rel="noopener noreferrer"
                className="text-terminal-amber hover:glow-text-gold transition-all duration-200"
              >
                https://calendly.com/privacy
              </a>
            </p>
          </section>

          {/* 5. Analyse-Tools */}
          <section>
            <h2 className="text-xl text-terminal-cyan font-semibold mb-4">{'>'} 5. Analyse-Tools und Werbung</h2>

            <h3 className="text-terminal-amber font-semibold mb-2">Matomo</h3>
            <p className="text-terminal-green/80 mb-4">
              Diese Website benutzt den Open Source Webanalysedienst Matomo. Mit Hilfe von Matomo sind wir
              in der Lage, Daten über die Nutzung unserer Website durch die Websitebesucher zu erfassen
              und zu analysieren. Die Nutzung dieses Analyse-Tools erfolgt auf Grundlage von Art. 6 Abs. 1
              lit. f DSGVO.
            </p>
            <p className="text-terminal-green/80 mb-2">
              <span className="text-terminal-green font-semibold">IP-Anonymisierung:</span> Bei der Analyse
              mit Matomo setzen wir IP-Anonymisierung ein. Hierbei wird Ihre IP-Adresse vor der Analyse
              gekürzt, sodass Sie Ihnen nicht mehr eindeutig zuordenbar ist.
            </p>
            <p className="text-terminal-green/80 mb-2">
              <span className="text-terminal-green font-semibold">Cookielose Analyse:</span> Wir haben
              Matomo so konfiguriert, dass Matomo keine Cookies in Ihrem Browser speichert.
            </p>
            <p className="text-terminal-green/80 mb-4">
              <span className="text-terminal-green font-semibold">Hosting:</span> Wir hosten Matomo
              ausschließlich auf unseren eigenen Servern, sodass alle Analysedaten bei uns verbleiben und
              nicht weitergegeben werden.
            </p>
          </section>

          {/* 6. Plugins und Tools */}
          <section>
            <h2 className="text-xl text-terminal-cyan font-semibold mb-4">{'>'} 6. Plugins und Tools</h2>

            <h3 className="text-terminal-amber font-semibold mb-2">Google Fonts (lokales Hosting)</h3>
            <p className="text-terminal-green/80 mb-4">
              Diese Seite nutzt zur einheitlichen Darstellung von Schriftarten so genannte Google Fonts,
              die von Google bereitgestellt werden. Die Google Fonts sind lokal installiert. Eine
              Verbindung zu Servern von Google findet dabei nicht statt. Weitere Informationen zu Google
              Fonts finden Sie unter{' '}
              <a
                href="https://developers.google.com/fonts/faq"
                target="_blank"
                rel="noopener noreferrer"
                className="text-terminal-amber hover:glow-text-gold transition-all duration-200"
              >
                https://developers.google.com/fonts/faq
              </a>
            </p>

            <h3 className="text-terminal-amber font-semibold mb-2">Podigee Podcast-Hosting</h3>
            <p className="text-terminal-green/80 mb-4">
              Wir nutzen den Podcast-Hosting-Dienst Podigee des Anbieters Podigee GmbH, Revaler Straße 28,
              10245 Berlin, Deutschland. Die Podcasts werden dabei von Podigee geladen oder über Podigee
              übertragen. Die Nutzung erfolgt auf Grundlage unserer berechtigten Interessen gem. Art. 6
              Abs. 1 lit. f. DSGVO. Podigee verarbeitet IP-Adressen und Geräteinformationen, um
              Podcast-Downloads/Wiedergaben zu ermöglichen. Weitere Informationen:{' '}
              <a
                href="https://www.podigee.com/de/about/privacy/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-terminal-amber hover:glow-text-gold transition-all duration-200"
              >
                https://www.podigee.com/de/about/privacy/
              </a>
            </p>
          </section>

          {/* Footer */}
          <div className="pt-6 border-t border-terminal-green/20 text-center">
            <Link
              href="/impressum"
              className="inline-flex items-center gap-2 text-terminal-green/70 hover:text-terminal-green transition-colors duration-200 text-sm"
            >
              <span>← Zum Impressum</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Back to Home */}
      <div className="mt-8 text-center">
        <Link
          href="/"
          className="text-xs text-terminal-green/40 hover:text-terminal-green transition-colors duration-200"
        >
          🎄 Zurück zur Christmas Code Challenge 🎄
        </Link>
      </div>
    </main>
  );
}







