#include <gtk/gtk.h>
#include <gio/gio.h>

#define PORTAL_BUS "org.freedesktop.portal.Desktop"
#define PORTAL_PATH "/org/freedesktop/portal/desktop"
#define PORTAL_IFACE "org.freedesktop.portal.Settings"
#define APPEARANCE_NS "org.freedesktop.appearance"
#define COLOR_SCHEME_KEY "color-scheme"

static GDBusConnection *connection;
static guint subscription;

static void apply_color_scheme(GVariant *value)
{
    GtkSettings *settings = gtk_settings_get_default();
    if (!settings)
        return;

    gboolean dark = value && g_variant_is_of_type(value, G_VARIANT_TYPE_UINT32)
        && g_variant_get_uint32(value) == 1;
    g_object_set(settings, "gtk-application-prefer-dark-theme", dark, NULL);
}

static void on_setting_changed(GDBusConnection *conn G_GNUC_UNUSED,
                               const gchar *sender G_GNUC_UNUSED,
                               const gchar *path G_GNUC_UNUSED,
                               const gchar *iface G_GNUC_UNUSED,
                               const gchar *signal G_GNUC_UNUSED,
                               GVariant *parameters,
                               gpointer user_data G_GNUC_UNUSED)
{
    const gchar *namespace_name;
    const gchar *key;
    GVariant *value;

    g_variant_get(parameters, "(&s&sv)", &namespace_name, &key, &value);
    if (g_strcmp0(namespace_name, APPEARANCE_NS) == 0 && g_strcmp0(key, COLOR_SCHEME_KEY) == 0)
        apply_color_scheme(value);
    g_variant_unref(value);
}

static void read_initial_color_scheme(void)
{
    GVariant *result = g_dbus_connection_call_sync(connection,
        PORTAL_BUS, PORTAL_PATH, PORTAL_IFACE, "Read",
        g_variant_new("(ss)", APPEARANCE_NS, COLOR_SCHEME_KEY),
        NULL, G_DBUS_CALL_FLAGS_NONE, 1000, NULL, NULL);

    if (!result)
        return;

    GVariant *value = NULL;
    g_variant_get(result, "(v)", &value);
    apply_color_scheme(value);
    g_variant_unref(value);
    g_variant_unref(result);
}

__attribute__((visibility("default")))
void gtk_module_init(gint *argc G_GNUC_UNUSED, gchar ***argv[] G_GNUC_UNUSED)
{
    connection = g_bus_get_sync(G_BUS_TYPE_SESSION, NULL, NULL);
    if (!connection)
        return;

    subscription = g_dbus_connection_signal_subscribe(connection,
        NULL, PORTAL_IFACE, "SettingChanged", PORTAL_PATH, NULL,
        G_DBUS_SIGNAL_FLAGS_NONE, on_setting_changed, NULL, NULL);

    read_initial_color_scheme();
}
