import type { VercelRequest, VercelResponse } from "@vercel/node";
import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);
const ADMIN_EMAIL = "heartbeatofgodf@gmail.com";
const FROM = "ILPC 2026 <noreply@heartbeatofgod.ca>";

/** Write registration to Supabase inquiries table (non-blocking). */
async function saveToSupabase(data: {
  fullName: string;
  email: string;
  ministry: string;
  designation: string;
  desire: string;
  submittedAt: string;
}): Promise<void> {
  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_ANON_KEY;
  if (!supabaseUrl || !supabaseKey) {
    console.warn("[supabase] SUPABASE_URL or SUPABASE_ANON_KEY not set — skipping DB write");
    return;
  }

  const payload = {
    full_name: data.fullName,
    email: data.email,
    type: "ilpc_2026_registration",
    status: "new",
    // Pack extra fields into message as structured JSON
    message: JSON.stringify({
      ministry: data.ministry,
      designation: data.designation,
      desire: data.desire,
      submitted_at: data.submittedAt,
    }),
  };

  const resp = await fetch(`${supabaseUrl}/rest/v1/inquiries`, {
    method: "POST",
    headers: {
      apikey: supabaseKey,
      Authorization: `Bearer ${supabaseKey}`,
      "Content-Type": "application/json",
      Prefer: "return=minimal",
    },
    body: JSON.stringify(payload),
  });

  if (!resp.ok) {
    const body = await resp.text();
    console.error(`[supabase] Insert failed (${resp.status}): ${body}`);
  } else {
    console.log(`[supabase] Registration saved for ${data.email}`);
  }
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { fullName, email, ministry, designation, desire } = req.body;

  if (!fullName || !email || !ministry || !designation || !desire) {
    return res.status(400).json({ error: "Missing required fields" });
  }

  const submittedAt = new Date().toISOString();

  // 1. Persist to Supabase (non-blocking — never fails the request)
  saveToSupabase({ fullName, email, ministry, designation, desire, submittedAt }).catch(
    (err) => console.error("[supabase] Unexpected error:", err)
  );

  try {
    // 2. Notify admin
    await resend.emails.send({
      from: FROM,
      to: ADMIN_EMAIL,
      subject: `New ILPC 2026 Registration — ${fullName}`,
      html: `
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto;background:#1A0533;color:#fff;padding:32px;border-radius:12px;">
          <h2 style="color:#C9972A;margin-bottom:24px;">New Registration — ILPC 2026</h2>
          <table style="width:100%;border-collapse:collapse;">
            <tr><td style="padding:8px 0;color:#B88FC7;font-size:13px;width:140px;">Full Name</td><td style="padding:8px 0;font-weight:bold;">${fullName}</td></tr>
            <tr><td style="padding:8px 0;color:#B88FC7;font-size:13px;">Email</td><td style="padding:8px 0;">${email}</td></tr>
            <tr><td style="padding:8px 0;color:#B88FC7;font-size:13px;">Ministry</td><td style="padding:8px 0;">${ministry}</td></tr>
            <tr><td style="padding:8px 0;color:#B88FC7;font-size:13px;">Designation</td><td style="padding:8px 0;">${designation}</td></tr>
            <tr><td style="padding:8px 0;color:#B88FC7;font-size:13px;vertical-align:top;">Desire</td><td style="padding:8px 0;">${desire}</td></tr>
          </table>
        </div>
      `,
    });

    // 3. Auto-reply to registrant
    await resend.emails.send({
      from: FROM,
      to: email,
      subject: "ILPC 2026 — Registration Confirmed!",
      html: `
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto;background:#1A0533;color:#fff;padding:32px;border-radius:12px;">
          <div style="text-align:center;margin-bottom:28px;">
            <h1 style="color:#C9972A;font-size:28px;margin:0;">ILPC 2026</h1>
            <p style="color:#B88FC7;font-size:13px;margin:4px 0 0;">Fresh Oil for a New Season</p>
          </div>
          <p style="font-size:16px;">Dear <strong style="color:#C9972A;">${fullName}</strong>,</p>
          <p style="color:#ccc;line-height:1.7;">
            Thank you for registering for <strong>ILPC 2026 — Fresh Oil for a New Season</strong>!
            Your registration has been received and your place is secured.
          </p>
          <div style="background:rgba(201,151,42,0.1);border:1px solid rgba(201,151,42,0.3);border-radius:10px;padding:20px;margin:24px 0;text-align:center;">
            <p style="margin:0;color:#C9972A;font-weight:bold;font-size:18px;">June 5–7, 2026</p>
            <p style="margin:6px 0 0;color:#B88FC7;font-size:14px;">HBG Ministry, Akute, Nigeria</p>
          </div>
          <p style="color:#ccc;line-height:1.7;">
            Come expecting a fresh encounter with God. We will be in touch with more details as the conference approaches.
          </p>
          <p style="color:#ccc;margin-top:32px;">God bless you,<br/>
          <strong style="color:#fff;">Pastor Amos Unogwu</strong><br/>
          <span style="color:#B88FC7;font-size:13px;">HBG Ministry | heartbeatofgod.ca</span></p>
        </div>
      `,
    });

    return res.status(200).json({ success: true });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: "Failed to send confirmation emails" });
  }
}
